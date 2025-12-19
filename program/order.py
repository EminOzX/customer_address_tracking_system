from PyQt5.QtWidgets import QMainWindow, QApplication
from ui_order import Ui_OrderWindow


class OrderWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_OrderWindow()
        self.ui.setupUi(self)