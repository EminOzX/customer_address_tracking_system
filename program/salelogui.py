from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QAbstractItemView
from PyQt5.QtCore import Qt


class SaleLogWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("salelogg.ui", self)
        self.setup_ui()

    def setup_ui(self):
        # Splitter orientation
        self.splitter.setOrientation(Qt.Horizontal)

        # TableView ayarları
        self.salesLogsTableView.setSortingEnabled(True)
        self.salesLogsTableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        # ReadOnly alanlar
        for name in [
            "lineEdit", "lineEdit_2", "lineEdit_3", "lineEdit_4",
            "lineEdit_5", "lineEdit_6", "lineEdit_7",
            "lineEdit_8", "lineEdit_9"
        ]:
            getattr(self, name).setReadOnly(True)

    def set_model(self, model):
        self.salesLogsTableView.setModel(model)
