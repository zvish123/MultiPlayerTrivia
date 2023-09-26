import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox)
from PyQt5.uic import loadUi
from functions import *


class BaseWindow(QDialog):
    def __init__(self, gui_design_file_name, relative_path=""):
        my_print(f"init {self.__class__.__name__}")
        super().__init__()
        loadUi(gui_design_file_name, self)
        load_css(self, relative_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BaseWindow("../design/signup.ui", "../")
    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec()
