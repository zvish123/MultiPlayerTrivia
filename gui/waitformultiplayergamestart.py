from PyQt5.uic import loadUi
import functions
from gui.basewindow import BaseWindow

class WaitForMPGameStart(BaseWindow):
    def __init__(self, main_window=None, relative_path=''):
        super().__init__("design/waitforstart.ui")
        # print("__init__ WaitForMPGameStart")
        # loadUi(relative_path + "design/waitforstart.ui", self)
        # functions.load_css(self)
        self.leaveButton.clicked.connect(self.leave_function)
        self.main_window = main_window
        if self.main_window is not None and self.main_window.client is not None:
            leave_game, question_id, question, answers = self.main_window.wait_for_next_mp_question()
            if leave_game:
                print("leave game")
                # add
            else:
                self.main_window.get_next_mp_question()

    def leave_function(self):
        print("leave_function pressed")