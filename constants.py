import logging


PORT = 6668
SERVER_IP = "127.0.0.1"
DELIMITER = "|"
LIST_DELIMITER = "@"

DIFFICULT_DICT = {
    "0": "Easy",
    "1": "Medium",
    "2": "Hard"
}

NUMBER_OF_QUESTIONS = 4
POINTS_PER_QUESTION = 5

MULTIPLY_FACTOR = 1

PUSH_BTN_CSS = "QPushButton{background-color: rgb(165, 165, 165);" \
               "font-size: 14pt;"\
               "color: rgb(230, 230, 230);"\
               "}"\
               "QPushButton::hover{"\
               "background-color: rgb(135, 135, 135);"\
               "border: none;"\
               "}"\
               "QPushButton::disabled {"\
               "background-color: black;"\
               "}"

LABEL_COLOR_CSS = 'QLabel {{font-size: 15pt; color:{}}}'

# print(LABEL_COLOR_CSS.format(' rgb(255, 0, 0)'))

LOG_LEVEL = logging.DEBUG