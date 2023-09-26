import logging

from PyQt5.QtWidgets import *
import random
import constants

@staticmethod
def load_css(window, relative_path=''):
    if relative_path == '':
        sshFile = "css/mystylesheet.css"
    else:
        sshFile = relative_path + "css/mystylesheet.css"
    with open(sshFile, "r") as fh:
        window.setStyleSheet(fh.read())

def shuffle_dict(my_dict, size):
    keys_list = list(my_dict.keys())
    random.shuffle(keys_list)
    ret_dict = {}
    for item in keys_list:
        ret_dict[item] = my_dict[item]
        size = size - 1
        if size == 0:
            return  ret_dict
    return ret_dict

def my_print(text, log_level=logging.DEBUG):
    # print(log_level, constants.LOG_LEVEL)
    if log_level >= constants.LOG_LEVEL:
        print(text)

if __name__ == '__main__':
    my_print(("hello"))
    my_print("hello debug", logging.DEBUG)
    my_print("hello info", logging.INFO)
    my_print("hello warning", logging.WARNING)
    my_print("hello error", logging.ERROR)
    my_print("hello fatal", logging.FATAL)
    my_print("hello critical", logging.CRITICAL)
