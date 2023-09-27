from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
import functions
from gui.readonlydelegate import ReadOnlyDelegate
from gui.basewindow import BaseWindow


class JoinMultiPlayerForm(BaseWindow):
    def __init__(self, main_window=None, relative_path=''):
        super().__init__("design/selecttocontinue.ui")
        # print("__init__ JoinMultiPlayerForm")
        # loadUi(relative_path + "design/selecttocontinue.ui", self)
        # functions.load_css(self)
        self.lbl_header.setText("Join multi player")
        self.tableWidget.setColumnWidth(0, 75)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 75)
        self.tableWidget.setColumnWidth(3, 150)
        self.tableWidget.selectionModel().selectionChanged.connect(self.on_selection_change)
        self.selectButton.clicked.connect(self.select_function)
        self.cancelButton.clicked.connect(self.cancel_function)
        self.main_window = main_window
        if self.main_window is not None and self.main_window.client is not None:
            # print("get_games_for_join")
            self.mp_games = self.main_window.client.get_games_for_join()
            self.fill_table_widget(self.mp_games)
            delegate = ReadOnlyDelegate(self)
            for i in range(self.tableWidget.rowCount()):
                self.tableWidget.setItemDelegateForRow(i, delegate)

    def fill_table_widget(self, games):
        # print(games)
        if len(games) > 0:
            row = 0
            self.tableWidget.setRowCount(len(games))
            for key, value in games.items():
                self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(key))
                self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(value[0]))
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(value[1]))
                self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(value[2]))
                row += 1
            self.tableWidget.selectRow(0)

    def select_function(self):
        # print("select_function pressed")
        p_reply = self.tableWidget.currentRow()
        selected_game_id = list(self.mp_games.keys())[p_reply]
        if self.main_window is not None and self.main_window.client is not None:
            game_id = self.main_window.client.join_mp_game(selected_game_id)
            # print("call wait_for_game_start")
            # self.wait_for_game_start(game_id)
            self.main_window.open_mp_question(game_id, None, "", [], False, False)

        # print("finish select_function")

    # def reportProgress(self, n):
    #     self.lbl_header.setText(f"waiting for multi player game [{n}] to start")
    #     self.lbl_header.setStyleSheet("color: red")
    #     self.tableWidget.setHidden(True)
    #     self.selectButton.setHidden(True)

    def cancel_function(self):
        # print("cancel_function pressed")
        if self.main_window is not None and self.main_window.client is not None:
            self.main_window.draw_background_picture()

    def on_selection_change(self):
        cur_row = self.tableWidget.currentRow()
        self.tableWidget.selectRow(cur_row)
