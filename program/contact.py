from PyQt5.QtWidgets import QMainWindow, QApplication
from contactui import Ui_ContactWindow


class ContactWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_ContactWindow()
        self.ui.setupUi(self)
