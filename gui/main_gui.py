import sys
from PyQt5.QtWidgets import (QMainWindow, QMenu, QMenuBar, QAction, QLabel)
from PyQt5.QtCore import Qt
from functions import *
from gui.loginform import Login, Signup
from gui.select_game_form import SelectGameForm
from PyQt5.QtGui import QPixmap
from gui.display_question_form import DisplayQuestion
from gui.game_result_form import GameResultForm
from gui.gameshistoryform import GamesHistoryForm
from gui.select_active_game import SelectActiveGameForm
from gui.Openmultiplayerform import OpenMultiPlayerForm
from gui.Joinmultiplayergame import JoinMultiPlayerForm
from gui.display_mp_game_question import DisplayMultiplayGameQuestion


class Window(QMainWindow):
    """Main Window."""
    def __init__(self, client=None, parent=None):
        """Initializer."""
        super().__init__(parent)
        load_css(self)
        self.setWindowTitle("Network Trivia Game")
        self.resize(800, 600)
        self.draw_background_picture()
        self._create_actions()
        self._create_menu_bar()
        self._connect_actions()
        self.client = client
        self.centralWidget = None

    def draw_background_picture(self):
        self.centralWidget = QLabel(self)
        pixmap = QPixmap('pictures/trivia2.jpg')
        pixmap1 = pixmap.scaled(self.width(), self.height())
        self.centralWidget.setPixmap(pixmap1)
        self.centralWidget.setMinimumSize(self.width(), self.height())
        self.setCentralWidget(self.centralWidget)

    def _create_menu_bar(self):
        self.main_menu_bar = self.menuBar()
        self.setMenuBar(self.main_menu_bar)
        login_menu = QMenu("&Login", self)
        self.main_menu_bar.addMenu(login_menu)
        login_menu.aboutToShow.connect(self.login)
        logout_menu = QMenu("&Logout", self)
        logout_menu.setDisabled(True)
        self.main_menu_bar.addMenu(logout_menu)

        logout_menu.aboutToShow.connect(self.logout)
        play_menu = QMenu("&Play", self)
        play_menu.setDisabled(True)
        self.main_menu_bar.addMenu(play_menu)

        play_menu.addAction(self.single_game_action)
        play_menu.addAction(self.continue_game_action)
        play_menu.addAction(self.game_history_action)
        play_menu.addAction(self.separator)
        play_menu.addAction(self.open_mp_action)
        play_menu.addAction(self.join_mp_action)
        play_menu.addAction(self.start_mp_action)
        play_menu.addAction(self.leave_mp_action)

        exit_menu = self.main_menu_bar.addMenu("&Exit")
        exit_menu.aboutToShow.connect(self.exit)
        self.user_menu = None
        self.add_user_to_menu(" "*20)

    def _create_actions(self):
        # Creating action using the first constructor
        self.single_game_action = QAction(self)
        self.single_game_action.setText("&Single game")
        # Creating actions using the second constructor
        self.continue_game_action = QAction("&Continue game", self)
        self.game_history_action = QAction("&Game History", self)
        self.open_mp_action = QAction("&Open multy player game", self)
        self.join_mp_action = QAction("&Join multy player game", self)
        self.start_mp_action = QAction("&Start multy player game", self)
        self.leave_mp_action = QAction("Leave multy player game", self)
        self.separator = QAction(self)
        self.separator.setSeparator(True)

    def _connect_actions(self):
        # Connect File actions
        self.single_game_action.triggered.connect(self.single_game)
        self.game_history_action.triggered.connect(self.display_games_history)
        self.continue_game_action.triggered.connect(self.continue_game)
        self.open_mp_action.triggered.connect(self.open_mp_game)
        self.join_mp_action.triggered.connect(self.join_mp_game)
        self.start_mp_action.triggered.connect(self.start_mp_game)
        self.leave_mp_action.triggered.connect(self.leave_mp_game)

    def add_user_to_menu(self, name):
        if self.user_menu is None:
            self.menuBr = QMenuBar(self.main_menu_bar)
            self.main_menu_bar.setCornerWidget(self.menuBr, Qt.TopRightCorner)
            self.user_menu = QMenu(self.menuBr)
            self.menuBr.setStyleSheet("QMenu  {color: rgb(0,100,0)} QMenuBar  {color: rgb(0,100,0)}"
                                         "  QMenuBar::item {color: rgb(0,100,0)}")
            self.user_menu.setTitle(name)
            self.menuBr.addAction(self.user_menu.menuAction())
        else:
            self.user_menu.setTitle(name)

    def disable_menu_option(self, name, disable=True):
        menus = {a.text(): a.menu() for a in self.main_menu_bar.actions() if a.menu()}
        try:
            menus[name].setDisabled(disable)
        except KeyError:
            print(f"Invalid Menu option name: {name}")

    def single_game(self):
        # Logic for creating a new file goes here...
        my_print('start single trivia game')
        self.centralWidget = SelectGameForm(self)
        self.setCentralWidget(self.centralWidget)
        # print(self.centralWidget.game_id)

    def continue_game(self):
        my_print('start continue_game')
        self.centralWidget = SelectActiveGameForm(self)
        self.setCentralWidget(self.centralWidget)

    def open_mp_game(self):
        my_print('start open_mp_game')
        self.centralWidget = OpenMultiPlayerForm(self)
        self.setCentralWidget(self.centralWidget)

    def join_mp_game(self):
        my_print('start join_mp_game')
        self.centralWidget = JoinMultiPlayerForm(self)
        self.setCentralWidget(self.centralWidget)

    def open_mp_question(self, game_id, question_id, question, answers, is_manager, is_start):
        my_print('start open_mp_question')
        # print(game_id, question_id, question, answers, is_manager, self)
        self.centralWidget = DisplayMultiplayGameQuestion(game_id, question_id, question, answers,
                                                          is_manager, is_start, self)
        self.setCentralWidget(self.centralWidget)

    def start_mp_game(self):
        my_print('start start_mp_game')
        if self.client is not None and self.client.mp_game_id is not None:
            self.centralWidget = DisplayMultiplayGameQuestion(self.client.mp_game_id, None, "", [], True, True, self)
            self.setCentralWidget(self.centralWidget)
        else:
            print("open a game before starting")

    def leave_mp_game(self):
        my_print("leave_mp_game")
        if self.client is not None and self.client.mp_game_id is not None:
            self.client.leave_mp_game()
            self.draw_background_picture()

    def login(self):
        my_print("login")
        self.centralWidget = Login(self)
        self.setCentralWidget(self.centralWidget)

    def signup(self):
        my_print("signup")
        self.centralWidget = Signup(self)
        self.setCentralWidget(self.centralWidget)

    def logout(self):
        # Logic for creating a new file goes here...
        my_print("logout")
        self.add_user_to_menu("")
        self.disable_menu_option('&Login', False)
        self.disable_menu_option('&Logout')
        self.disable_menu_option('&Play')
        if self.client is not None:
            self.client.logout()
            self.draw_background_picture()

    def exit(self):
        if self.client is not None:
            self.client.handle_exit()
            sys.exit()

    def display_question_form(self, game_id,  question_id, question, answers):
        self.centralWidget = DisplayQuestion(game_id,  question_id, question, answers, self)
        self.setCentralWidget(self.centralWidget)

    def display_game_result(self, game_id):
        self.centralWidget = GameResultForm(game_id, "", "", self)
        self.setCentralWidget(self.centralWidget)

    def display_games_history(self):
        self.centralWidget = GamesHistoryForm(self)
        self.setCentralWidget(self.centralWidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
