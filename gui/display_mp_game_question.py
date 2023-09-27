import sys
from PyQt5 import QtWidgets
import textwrap
from functions import *
from gui.display_question_form import  DisplayQuestion
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from threading import Lock


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, game_id, my_window, is_manager=False, is_start=False):
        super().__init__()
        my_print("Worker init")
        self.game_id = game_id
        self.my_window = my_window
        self.is_manager = is_manager
        self.is_start = is_start
        self.lock = Lock()

    def run(self):
        """Long-running task."""
        my_print("start running Worker")
        self.lock.acquire()
        # self.progress.emit(int(self.game_id))
        leave_game, question_id, question, answers = self.my_window.main_window.client.handle_next_mp_question()
        # my_print("run -> handle_next_mp_question", leave_game, question_id, question, answers)
        self.my_window.question_id = question_id
        self.my_window.question = question
        self.my_window.answers = answers
        self.progress.emit(int(self.game_id))
        self.finished.emit()
        my_print("finish running Worker")
        self.lock.release()


class DisplayMultiplayGameQuestion(DisplayQuestion):
    def __init__(self, game_id, question_id, question, answers, is_manager, is_start,
                 main_window=None, relative_path=''):
        super().__init__(game_id, question_id, question, answers, main_window, relative_path)
        # my_print("__init__ DisplayMultiplayGameQuestion")
        self.is_start = is_start
        self.is_manager = is_manager
        self.fill_mp_fields(True)

        if question_id is None:
            if self.is_start:
                to_start = self.main_window.client.start_mp_game()
                if to_start:
                    self.wait_for_next_question(game_id)
                    self.is_start = False
            else:
                self.wait_for_next_question(game_id)

    def fill_mp_fields(self, in_init):
        self.fill_fields()
        # print("DisplayMultiplayGameQuestion fill_fields")
        if self.is_manager:
            self.next_btn.setEnabled(False)
        else:
            self.next_btn.setHidden(True)
        if in_init:
            # print("in_init")
            gid = str(self.game_id)
            text = f"Waiting for multi play game [{gid}] to start"
            question1 = textwrap.fill(text, width=45)
            self.question_lbl.setText(question1)
            self.question_lbl.setStyleSheet("color: red")
            self.tableWidget.setHidden(True)
            self.select_btn.setHidden(True)
        elif self.question_id is not None:
            # print(f"in question {self.question_id}")
            self.question_lbl.setStyleSheet("color: rgb(255, 140, 94)")
            self.tableWidget.setHidden(False)
            self.select_btn.setHidden(False)
            self.select_btn.setEnabled(True)
            self.next_btn.setEnabled(False)
            self.lbl_reply.setText("")
            self.lbl_reply.setHidden(True)
        elif self.question_id is None or self.question_id == 'None':
            print("no more questions")
            self.lbl_reply.setHidden(True)
            self.tableWidget.setHidden(True)
            self.select_btn.setHidden(True)
            self.leave_btn.setHidden(True)
            self.next_btn.setEnabled(True)
            self.next_btn.setHidden(False)
            self.next_btn.setText("Ok")
            if self.is_manager:
                cmd, score = self.main_window.client.handle_multi_player_game_end()
            else:
                cmd, score = self.main_window.client.handle_multi_player_game_end(True)
            self.question_lbl.setText(f"Game score: {score}")

    def wait_for_next_question(self, game_id):
        # print(game_id, self.main_window, self.is_manager, self.is_start)
        # print("wait_for_next_question")
        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = Worker(game_id, self, self.is_manager, self.is_start)
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_display)
        # Start the thread
        # print("start thread")
        self.thread.start()

    def update_display(self, game_id):
        # print("update display")
        self.fill_mp_fields(False)

    def select_function(self):
        # print("start mp select_function")
        p_reply = self.tableWidget.currentRow() + 1
        if self.main_window is not None and self.main_window.client is not None:
            is_notified = self.main_window.client.notify_mp_answer(self.question_id, self.question, p_reply)
            self.select_btn.setEnabled(False)
            self.next_btn.setEnabled(True)
            self.is_start = False
            self.lbl_reply.setText("Wait for all players responses")
            self.lbl_reply.setHidden(False)
            if not self.is_manager:
                self.wait_for_next_question(self.game_id)
            # self.main_window.open_mp_question(self.game_id, None, "", [], self.is_manager, False)

    def next_function(self):
            # print("start mp next_function")
        try:
            if self.question_id is None:
                self.main_window.draw_background_picture()
            elif self.main_window is not None and self.main_window.client is not None:
                # print(f"{'next_function'} {self.question_id}")
                can_continue = self.main_window.client.can_moveto_next_mp_question()
                # print(can_continue)
                # print(self.__dir__())
                if can_continue:
                    self.lbl_reply.setHidden(True)
                    self.select_btn.setEnabled(True)
                    self.next_btn.setEnabled(False)
                    self.wait_for_next_question(self.game_id)
                    # print("call to ask_for_next_mp_question")
                    # next mp question
                    #wait for mp question
                    self.main_window.client.ask_for_next_mp_question()
        except Exception as e:
            my_print(e, logging.ERROR)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game_id = "10"
    question_id = "1"
    # question_id = None
    question = "Which class of animals are newts members of?"
    answers = ['Amphibian', 'Reptiles', 'Mammals', 'Fish']
    main_window = DisplayMultiplayGameQuestion(game_id, question_id, question, answers, True, False, None, "../")
    widget = QtWidgets.QStackedWidget()
    widget.setFixedWidth(640)
    widget.setFixedHeight(640)
    widget.addWidget(main_window)
    widget.show()
    app.exec_()