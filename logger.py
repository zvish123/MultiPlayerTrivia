import logging
from threading import Lock


class Logger:
    def __init__(self, file_name, level=logging.INFO, print_screen=False, lock=None):
        logging.basicConfig(filename=file_name, filemode='w',
                            format='%(asctime)s - %(levelname)-10s - %(message)s', level=level)
        self.print_screen = print_screen
        self.lock = lock

    def write(self, message, level=logging.INFO):
        if self.lock is not None:
            self.lock.acquire()
        if level == logging.DEBUG:
            logging.debug(message)
        elif level == logging.INFO:
            logging.info(message)
        elif level == logging.WARNING:
            logging.warning(message)
        elif level == logging.ERROR:
            logging.error(message)
        elif level == logging.CRITICAL:
            logging.critical(message)
        else:
            level = logging.INFO
            logging.info(message)
        if self.lock is not None:
            self.lock.release()
        if self.print_screen:
            print(logging.getLevelName(level), ":", message)


if __name__ == '__main__':
    my_logger = Logger("log/example.log", logging.DEBUG)
    my_logger.write("debug message", logging.DEBUG)
    my_logger.write("info message", logging.INFO)
    my_logger.write("warning message", logging.WARNING)
    my_logger.write("error message", logging.ERROR)
    my_logger.write("critical message", logging.CRITICAL)
    my_logger.write("mistake message", "a")
