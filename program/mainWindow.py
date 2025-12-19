from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
from PyQt5.QtCore import Qt
from order import OrderWindow


class OrdersWindow(QMainWindow):
    def _init_(self):
        super()._init_()

        # ✅ UI'yi kesin yükle (form tipi fark etmez)
        uic.loadUi("order.ui", self)

        # ✅ UI gerçekten yüklendi mi? (yüklenmezse burada patlar)
        if not hasattr(self, "tblOrders"):
            QMessageBox.critical(self, "Hata", "UI yüklenmedi: tblOrders bulunamadı. order.ui yanlış olabilir.")
            return

        # ✅ DB bağlantısı
        if not self.create_connection():
            return

        # ✅ Table ayarları
        self.tblOrders.setSelectionBehavior(self.tblOrders.SelectRows)
        self.tblOrders.setSelectionMode(self.tblOrders.SingleSelection)
        self.tblOrders.setEditTriggers(self.tblOrders.NoEditTriggers)

        self.model = QSqlQueryModel(self)
        self.tblOrders.setModel(self.model)

        # ✅ Buton bağla (objectName'ler bu isimde olmalı)
        self.btnDeliverOrder.clicked.connect(self.deliver_selected_order)
        self.btnRefresh.clicked.connect(self.load_orders)

        # İlk yükleme
        self.load_orders()

    def create_connection(self):
        db = QSqlDatabase.addDatabase("QODBC")
        db.setDatabaseName(
            "Driver={SQL Server};"
            "Server=localhost;"  # gerekirse .\\SQLEXPRESS
            "Database=customer_address_tracking_system;"
            "Trusted_Connection=yes;"
        )
        if not db.open():
            QMessageBox.critical(self, "DB Hatası", db.lastError().text())
            return False
        return True

    def load_orders(self):
        sql = """
        SELECT order_id, user_id, address_id, branch_id, order_status, payment_method, total_amount, created_at
        FROM orders
        ORDER BY created_at DESC
        """
        self.model.setQuery(sql)

        self.model.setHeaderData(0, Qt.Horizontal, "Order ID")
        self.model.setHeaderData(4, Qt.Horizontal, "Status")
        self.model.setHeaderData(7, Qt.Horizontal, "Created At")
        self.tblOrders.resizeColumnsToContents()

    def deliver_selected_order(self):
        index = self.tblOrders.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "Uyarı", "Lütfen tablodan bir sipariş seç.")
            return

        row = index.row()
        order_id = int(self.model.index(row, 0).data())

        q = QSqlQuery()
        q.prepare("UPDATE orders SET order_status=? WHERE order_id=?")
        q.addBindValue("delivered")
        q.addBindValue(order_id)

        if not q.exec_():
            QMessageBox.critical(self, "Hata", q.lastError().text())
            return

        QMessageBox.information(self, "Başarılı", f"{order_id} teslim edildi olarak güncellendi.")
        self.load_orders()