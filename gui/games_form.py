import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QDialog, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox, QStyledItemDelegate)
from PyQt5.uic import loadUi
from gui.readonlydelegate import ReadOnlyDelegate

# class ReadOnlyDelegate(QStyledItemDelegate):
#     def createEditor(self, perant, option, index):
#         print("create_editor fire")
#         return

class MainWindow(QDialog):
    def __init__(self):
        super().__init__()
        loadUi('../design/gameslist.ui', self)
        self.tableWidget.setColumnWidth(0, 75)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(3,150)
        self.tableWidget.selectionModel().selectionChanged.connect(self.on_selection_change)
        self.load_data()
        delegate = ReadOnlyDelegate(self)
        # print(self.tableWidget.rowCount())
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.setItemDelegateForRow(i, delegate)

    def load_data(self):
        games = [{"game_id": 10, "category": "Music", "difficulty": "medium", "number_of_questions": 10},
                 {"game_id": 12, "category": "History", "difficulty": "hard", "number_of_questions": 12},
                 {"game_id": 15, "category": "Sport", "difficulty": "hard", "number_of_questions": 8},
                 {"game_id": 18, "category": "Computer science", "difficulty": "easy", "number_of_questions": 10}]
        row = 0
        self.tableWidget.setRowCount(len(games))
        for game in games:
            self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(game["game_id"])))
            self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(game["category"]))
            self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(game["difficulty"]))
            self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(game["number_of_questions"])))
            row += 1
    def on_selection_change(self, selected):
        # for ix in selected.indexes():
            # print(f"selected cell location Row: {ix.row()} Column: {ix.column()}")
            # self.tableWidget.selectRow(ix.row());
        cur_row = self.tableWidget.currentRow()
        # print("a", cur_row)
        self.tableWidget.selectRow(cur_row);


app = QApplication(sys.argv)
main_window = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(main_window)
widget.setFixedWidth(850)
widget.setFixedHeight(850)
widget.show()
app.exec_()
