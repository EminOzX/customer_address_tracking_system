from PyQt5.QtWidgets import QMainWindow, QApplication
from registerui import Ui_RegisterWindow


class RegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_RegisterWindow()
        self.ui.setupUi(self)
