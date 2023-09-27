from PyQt5.uic import loadUi
import functions
from gui.basewindow import BaseWindow


class OpenMultiPlayerForm(BaseWindow):
    def __init__(self, main_window=None, relative_path=''):
        super().__init__("design/selecttriviagame.ui")
        # print("__init__ OpenMultiPlayerForm")
        # loadUi(relative_path + "design/selecttriviagame.ui", self)
        # functions.load_css(self)
        self.lbl_header.setText("Open multi player game")
        self.approveButton.clicked.connect(self.approve_function)
        self.main_window = main_window
        self.approveButton.setText("Open game")
        if self.main_window is not None and self.main_window.client is not None:
            categories = self.main_window.client.get_categories()
            difficulties = self.main_window.client.get_difficulties()
            number_of_questions = self.main_window.client.get_number_of_questions()

            for category in categories:
                self.category_cb.addItem(category)
            for difficulty in difficulties:
                self.difficulty_cb.addItem(difficulty)
            self.number_of_questions.setReadOnly(True)
            self.number_of_questions.setText(number_of_questions)
    def approve_function(self):
        # print("start approve_function")
        category = self.category_cb.currentText()
        difficulty = self.difficulty_cb.currentText()
        number_of_questions = int(self.number_of_questions.text())
        if self.main_window is not None and self.main_window.client is not None:
            difficulty_key = self.main_window.client.get_difficulty_key(difficulty)
            game_id = self.main_window.client.open_game(category, difficulty_key, number_of_questions)
            # print(game_id)
            # self.main_window.start_mp_action.setTitle(f"&Start multy player game [{game_id}]")
            self.main_window.draw_background_picture()


