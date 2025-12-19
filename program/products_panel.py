from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from connection import get_connection


class ProductWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("product_panel.ui", self)
        self.setup_ui()

    def setup_ui(self):
        """Program ilk açıldığında çalışacak başlangıç ayarları."""
        # Category doldur
        self.categorycombo.addItems(["food", "drink", "tech"])

        # ✅ VENDOR COMBO'YU DB'DEN DOLDUR
        self.vendorCombo.clear()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT vendor_id, vendor_name FROM vendors")
        for vendor_id, vendor_name in cur.fetchall():
            self.vendorCombo.addItem(vendor_name, vendor_id)
        conn.close()

        # Tablonun başlıklarını ayarla
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels([
            "Product ID", "Name", "Vendor", "Quantity",
            "Category", "Unit Price", "Total Price"
        ])

        # Total price sadece gösterim amaçlı
        self.totalPriceInput.setReadOnly(True)
