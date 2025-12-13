from PyQt5.QtWidgets import QMainWindow, QApplication
from ui_customerRepresentative import Ui_customerRepresentative


class RepresentativeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_customerRepresentative()
        self.ui.setupUi(self)