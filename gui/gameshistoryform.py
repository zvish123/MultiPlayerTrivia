from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QDialog, QTableWidgetItem)
from PyQt5.uic import loadUi
import constants
import functions
from gui.readonlydelegate import ReadOnlyDelegate


# class ReadOnlyDelegate(QStyledItemDelegate):
#     def createEditor(self, perant, option, index):
#         print("create_editor fire")
#         return

class GamesHistoryForm(QDialog):
    def __init__(self, main_window=None, relative_path=''):
        super().__init__()
        print("__init__ GamesHistoryForm")
        loadUi(relative_path + "design/gameshistory.ui", self)
        functions.load_css(self)
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setColumnWidth(1, 75)
        self.tableWidget.setColumnWidth(2, 150)
        self.tableWidget.setColumnWidth(3, 75)
        self.tableWidget.setColumnWidth(4, 125)
        self.tableWidget.setColumnWidth(5, 75)
        self.tableWidget.selectionModel().selectionChanged.connect(self.on_selection_change)
        self.main_window = main_window
        # self.okButton.setStyleSheet(constants.PUSH_BTN_CSS)
        self.okButton.clicked.connect(self.ok_function)
        games = self.main_window.client.games_history()
        self.fill_table_widget(games)
        delegate = ReadOnlyDelegate(self)
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.setItemDelegateForRow(i, delegate)

    def fill_table_widget(self, games):
        print(games)
        # if len(games) > 0:
        #     header = QTableWidgetItem()
        #     header.setText(games[0])
        #     self.tableWidget.setHorizontalHeaderItem(0, header)
        # print("after setHorizontalHeaderItem")
        if len(games) > 0:
            row = 0
            self.tableWidget.setRowCount(len(games))
            for key, value in games.items():
                self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(value[0]))
                self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(key))
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(value[1]))
                self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(value[2]))
                self.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(value[3]))
                self.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(value[4]))
                row += 1
            self.tableWidget.selectRow(0)
        print("finish fill_table_widget")

    def ok_function(self):
        print("ok_function pressed")
        if self.main_window is not None and self.main_window.client is not None:
            self.main_window.draw_background_picture()

    def on_selection_change(self):
        cur_row = self.tableWidget.currentRow()
        self.tableWidget.selectRow(cur_row)
