from PyQt5.QtWidgets import QMainWindow, QApplication
from customerpanelui import Ui_CustomerWindow


class CustomerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_CustomerWindow()
        self.ui.setupUi(self)
