import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog)
from PyQt5.uic import loadUi
import constants
import functions
from gui.readonlydelegate import ReadOnlyDelegate


class SelectActiveGameForm(QDialog):
    def __init__(self, main_window=None, relative_path=''):
        super().__init__()
        print("__init__ SelectActiveGameForm")
        loadUi(relative_path + "design/selecttocontinue.ui", self)
        functions.load_css(self)
        self.tableWidget.setColumnWidth(0, 75)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 75)
        self.tableWidget.setColumnWidth(3, 150)
        self.tableWidget.selectionModel().selectionChanged.connect(self.on_selection_change)
        self.selectButton.clicked.connect(self.select_function)
        # self.selectButton.setStyleSheet(constants.PUSH_BTN_CSS)
        self.cancelButton.clicked.connect(self.cancel_function)
        # self.cancelButton.setStyleSheet(constants.PUSH_BTN_CSS)
        self.main_window = main_window
        if self.main_window is not None and self.main_window.client is not None:
            self.active_games = self.main_window.client.get_active_player_games()
            self.fill_table_widget(self.active_games)
            delegate = ReadOnlyDelegate(self)
            for i in range(self.tableWidget.rowCount()):
                self.tableWidget.setItemDelegateForRow(i, delegate)

    def fill_table_widget(self, active_games):
        print(active_games)
        if len(active_games) > 0:
            row = 0
            self.tableWidget.setRowCount(len(active_games))
            for key, value in active_games.items():
                self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(key))
                self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(value[0]))
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(value[1]))
                self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(value[2]))
                row += 1
            self.tableWidget.selectRow(0)
        print("finish fill_table_widget")

    def select_function(self):
        print("select_function pressed")
        p_reply = self.tableWidget.currentRow()
        selected_game_id = list(self.active_games.keys())[p_reply]
        if self.main_window is not None and self.main_window.client is not None:
            game_id = self.main_window.client.ask_to_continue_game(selected_game_id)
            question_id, question, answers = self.main_window.client.get_next_question(game_id)
            self.main_window.display_question_form(game_id, question_id, question, answers)

    def cancel_function(self):
        print("cancel_function pressed")
        if self.main_window is not None and self.main_window.client is not None:
            self.main_window.draw_background_picture()

    def on_selection_change(self):
        cur_row = self.tableWidget.currentRow()
        self.tableWidget.selectRow(cur_row)