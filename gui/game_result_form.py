import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QDialog, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox)
from PyQt5.uic import loadUi
import constants
import functions


class GameResultForm(QDialog):
    def __init__(self, game_id, category="", difficulty="", main_window=None, relative_path=''):
        super().__init__()
        print("__init__ GameResultForm")
        loadUi(relative_path + "design/gameresult.ui", self)
        functions.load_css(self)
        self.main_window = main_window
        if self.main_window is not None and self.main_window.client is not None:
            score = self.main_window.client.game_score(game_id)
            self.lbl_game_id.setText(str(game_id))
            self.lbl_category.setText(category)
            self.lbl_difficulty.setText(difficulty)
            self.lbl_score.setText(score)
        self.okButton.clicked.connect(self.ok_function)
        # self.okButton.setStyleSheet(constants.PUSH_BTN_CSS)

    def ok_function(self):
        print("ok_function run")
        if self.main_window is not None and self.main_window.client is not None:
            self.main_window.draw_background_picture()