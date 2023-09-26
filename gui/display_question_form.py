import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QDialog, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox)
from PyQt5.uic import loadUi
import textwrap
import constants
import functions


class DisplayQuestion(QDialog):
    def __init__(self, game_id, question_id, question, answers, main_window=None, relative_path=''):
        super().__init__()
        print("__init__ DisplayQuestion")
        loadUi(relative_path + "design/gamequestion.ui", self)
        functions.load_css(self, relative_path)
        self.tableWidget.setColumnWidth(0, 440)
        self.leave_btn.clicked.connect(self.leave_function)

        self.select_btn.clicked.connect(self.select_function)
        self.lbl_reply.setHidden(True)
        self.lbl_correct.setHidden(True)
        self.lbl_correct_reply.setHidden(True)

        self.next_btn.clicked.connect(self.next_function)
        self.next_btn.setEnabled(False)
        self.main_window = main_window
        self.current_question = 1
        self.game_id = game_id
        self.question_id = question_id
        self.question = question
        self.answers = answers
        self.fill_fields()

    def fill_fields(self):
        print("fill_fields")
        if self.question_id is not None:
            question1 = textwrap.fill(self.question, width=45)
            self.question_lbl.setStyleSheet("color: rgb(255, 140, 94)")
            self.question_lbl.setText(question1)
            self.fill_table_widget(self.answers)
            self.tableWidget.setHidden(False)
            self.select_btn.setHidden(False)
        else:
            print("fill_fields do nothing")
        # else:
        #     gid = str(self.game_id)
        #     text = f"Waiting for multi play game [{gid}] to start"
        #     # print(text)
        #     question1 = textwrap.fill(text, width=45)
        #     self.question_lbl.setText(question1)
        #     self.question_lbl.setStyleSheet("color: red")


    def fill_table_widget(self, answers):
        if len(answers) > 0:
            row = 0
            self.tableWidget.setRowCount(len(answers))
            for answer in answers:
                # self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(row+1)))
                self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(answer))
                row += 1
            self.tableWidget.selectRow(0)
    def select_function(self):
        print("start select_function")
        p_reply = self.tableWidget.currentRow()+1
        if self.main_window is not None and self.main_window.client is not None:
            is_correct, correct_ans_txt = self.main_window.client.check_question_answer(self.game_id, self.question_id,
                                                                                        self.question, p_reply )
            # print(is_correct, correct_ans_txt)
            self.lbl_reply.setHidden(False)
            if is_correct:
                reply = "Correct"
                self.lbl_reply.setStyleSheet(constants.LABEL_COLOR_CSS.format('rgb(0, 255, 0)'))
            else:
                reply = "Incorrect"
                self.lbl_reply.setStyleSheet(constants.LABEL_COLOR_CSS.format('rgb(255, 0, 0)'))
                self.lbl_correct.setHidden(False)
                self.lbl_correct_reply.setHidden(False)
                self.lbl_correct_reply.setText(correct_ans_txt)
            self.lbl_reply.setText(reply)

            self.next_btn.setEnabled(True)
            self.select_btn.setEnabled(False)


    def next_function(self):
        print("start next_function")
        question_id, question, answers = self.main_window.client.get_next_question(self.game_id)
        if question_id is not None:
            self.main_window.display_question_form(self.game_id, question_id, question, answers)
        else:
            self.main_window.display_game_result(self.game_id)

    def leave_function(self):
        print("leave_function pressed")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game_id = "10"
    question_id = "1"
    question = "Which class of animals are newts members of?"
    answers = ['Amphibian', 'Reptiles', 'Mammals', 'Fish']
    main_window = DisplayQuestion(game_id, question_id, question, answers, None, "../")
    widget = QtWidgets.QStackedWidget()
    widget.setFixedWidth(640)
    widget.setFixedHeight(640)
    widget.addWidget(main_window)
    widget.show()
    app.exec_()