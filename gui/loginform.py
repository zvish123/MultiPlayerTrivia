import sys
from PyQt5 import QtWidgets
from gui.basewindow import BaseWindow
from functions import *


class Signup(BaseWindow):
	def __init__(self, main_window=None):
		super().__init__("design/signup.ui")
		self.signupButton.clicked.connect(self.signup_function)
		self.password.setEchoMode(QtWidgets.QLineEdit.Password)
		self.password_2.setEchoMode(QtWidgets.QLineEdit.Password)
		self.main_window = main_window

	def signup_function(self):
		my_print("start signup_function")
		user_name = self.user_name.text()
		password = self.password.text()
		password2 = self.password_2.text()
		if password == password2:
			if self.main_window is None:
				widget.setCurrentIndex(widget.currentIndex() - 1)
			else:
				if self.main_window.client is None:
					result = 1
				else:
					result = self.main_window.client.signin(user_name, password)
				if result == 1:
					self.main_window.centralWidget = Login(self.main_window)
					self.main_window.setCentralWidget(self.main_window.centralWidget)
				elif result == 0:
					self.lbl_error.setText("you already logged in")
				else:
					self.lbl_error.setText("user already exists")
		else:
			self.lbl_error.setText("unsuccessful signup")


class Login(BaseWindow):
	def press_event(self):
		self.info_message.setText(' ')

	def __init__(self, main_window=None):
		super().__init__("design/login.ui")
		self.lbl_header.setProperty("cssClass", "large")
		self.loginButton.clicked.connect(self.loginFunction)
		self.password.setEchoMode(QtWidgets.QLineEdit.Password)
		self.createAccountBtn.clicked.connect(self.goto_signup)
		self.main_window = main_window

	def mousePressEvent(self, e):
		self.clean_fields()

	def loginFunction(self):
		user_name = self.user_name.text()
		password = self.password.text()
		if self.main_window.client is None:
			result = 1
		else:
			result = self.main_window.client.login(user_name, password)
		if result == 1:
			my_print(f"successfully logged in [{user_name}, {password}]")
			if self.main_window is not None:
				self.main_window.add_user_to_menu("hello " + user_name)
				self.main_window.draw_background_picture()
				self.main_window.disable_menu_option('&Login')
				self.main_window.disable_menu_option('&Logout', False)
				self.main_window.disable_menu_option('&Play', False)
			self.close()
		elif result == 0:
			self.lbl_error.setText('You already logged in')
		elif result == -1:
			self.lbl_error.setText('Incorrect user or password')
		elif result == -2:
			self.lbl_error.setText("Can't login twice")

	def clean_fields(self):
		self.info_message.setText(' ')
		self.user_name.setText('')
		self.password.setText('')

	def goto_signup(self):

		if self.main_window is None:
			signup_window = Signup()
			widget.addWidget(signup_window)
			widget.setCurrentIndex(widget.currentIndex()+1)
		else:
			self.main_window.signup()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	main_window = Login()
	widget = QtWidgets.QStackedWidget()
	widget.setFixedWidth(480)
	widget.setFixedHeight(620)
	widget.addWidget(main_window)
	widget.show()
	app.exec_()
