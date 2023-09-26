import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QDialog, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox)
from PyQt5.uic import loadUi
import constants
import functions


class WaitForMPGameStart(QDialog):
    def __init__(self, main_window=None, relative_path=''):
        super().__init__()
        print("__init__ WaitForMPGameStart")
        loadUi(relative_path + "design/waitforstart.ui", self)
        functions.load_css(self)
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