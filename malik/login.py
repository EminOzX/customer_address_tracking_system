from PyQt5.QtWidgets import QMainWindow, QApplication
from loginui import Ui_LoginWindow


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
