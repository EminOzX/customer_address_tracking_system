from PyQt5.QtGui import QRegularExpressionValidator, QStandardItemModel, QStandardItem
from PyQt5.QtCore import QRegularExpression, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QAbstractItemView, QTableWidgetItem
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel

import smtplib
from email.message import EmailMessage

from login import LoginWindow
from register import RegisterWindow
from customerpanel import CustomerWindow
from contact import ContactWindow
from order import OrderWindow
from products_panel import ProductWindow
from salelogui import SaleLogWindow
import pyodbc
import re
from datetime import datetime
from connection import get_connection

from dudumainWindow import RepresentativeWindow
from ui_customerRepresentative import Ui_customerRepresentative

conn = get_connection()
cursor = conn.cursor()



MESSAGES = [
    {
        "customer_id": 1,
        "email": "test1@mail.com",
        "complaint": "Product arrived broken",
        "feedback": None
    },
    {
        "customer_id": 2,
        "email": "test2@mail.com",
        "complaint": "Late delivery",
        "feedback": None
    },
    {
        "customer_id": 3,
        "email": "beyzadudu.keskin@stu.fsm.edu.tr",
        "complaint": "Wrong product sent",
        "feedback": None
    }
]


class Controller:
    def __init__(self):
        self.row = None
        self.general_id = None
        self.pattern = re.compile(r'^.{3,}$')
        self.login = LoginWindow()
        self.register = RegisterWindow()
        self.customer = CustomerWindow()
        self.contact = ContactWindow()
        self.courier = OrderWindow()

        # Customer Representive start ------------
        self.customer_representive = RepresentativeWindow()
        tbl = self.customer_representive.ui.tbl_customer
        self.customer_representive.ui.btn_banRequest.clicked.connect(self.ban_customer)
        tbl.setEditTriggers(tbl.NoEditTriggers)
        tbl.setSelectionBehavior(tbl.SelectRows)
        tbl.setSelectionMode(tbl.SingleSelection)
        tbl.setEnabled(True)
        self.selectedEmail = None
        tbl.cellClicked.connect(self.on_row_clicked)
        self.customer_representive.ui.btn_sendFeedback.clicked.connect(self.send_feedback)

        self.load_customers()
        # Customer Representive end ------------

        # Product start
        
        self.salelog = SaleLogWindow()
        self.product = ProductWindow()
        self.selected_product_id = None

        self.product.btnAddProduct.clicked.connect(self.add_product)
        self.product.btnUpdateProduct.clicked.connect(self.update_product)
        self.product.btnDeleteProduct.clicked.connect(self.delete_product)
        self.product.btnCleanForm.clicked.connect(self.clear_form)
        self.product.tableWidget.itemSelectionChanged.connect(self.on_table_selection_changed)
        self.load_products()
        self.load_vendors()

        self.product.productIdInput.setReadOnly(True)
        # Product end

        #Courier panel codes ------
        self.courier = OrderWindow()

        tv = self.courier.ui.tblOrders
        tv.setSelectionBehavior(tv.SelectRows)
        tv.setSelectionMode(tv.SingleSelection)
        tv.setEditTriggers(tv.NoEditTriggers)
        self.model = QStandardItemModel(self.courier)
        tv.setModel(self.model)
        self.courier.ui.btnRefresh.clicked.connect(self.load_orders)
        self.courier.ui.btnTakeOrder.clicked.connect(self.take_selected_order)
        self.courier.ui.btnDeliverOrder.clicked.connect(self.deliver_selected_order)
        self.load_orders()

        #Courier panel codes ------
        
        #Contact panel codes
        self.contact.ui.pushButton_Send.clicked.connect(self.send_complaint_message)
        self.contact.ui.pushButton_Back.clicked.connect(self.back_to_customer)
        self.customer.ui.comboBox_City.currentIndexChanged.connect(self.list_districts)
        #Customer panel codes
        self.customer.ui.pushButton_Refresh.clicked.connect(self.refresh_tables)
        self.customer.ui.pushButton_Order.clicked.connect(self.give_order)
        self.customer.ui.pushButton_Contact.clicked.connect(self.show_contact)
        self.customer.ui.pushButton_Login.clicked.connect(self.back_to_login)
        self.customer.ui.pushButton_Address.clicked.connect(self.add_address)

        self.customer.ui.tableView_Product.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.customer.ui.tableView_Product.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.customer.ui.tableView_Address.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.customer.ui.tableView_Address.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # Login panel codes
        self.login.ui.pushButton_Login.clicked.connect(self.sign_in)
        self.login.ui.pushButton_Register.clicked.connect(self.show_register)
       
        # Register panel codes 
        self.register.ui.lineEdit_Fname.setValidator(QRegularExpressionValidator(
            QRegularExpression("^[A-Za-z]*$")
        ))
        self.register.ui.lineEdit_Lname.setValidator(QRegularExpressionValidator(
            QRegularExpression("^[A-Za-z]*$")
        ))
        self.register.ui.lineEdit_Username.setValidator(QRegularExpressionValidator(
            QRegularExpression("^[A-Za-z0-9]*$")
        ))
        
        self.register.ui.lineEdit_Phone.setValidator(QRegularExpressionValidator(
            QRegularExpression("^[0-9]*$")
        ))
        self.register.ui.pushButton_Login.clicked.connect(self.show_login)
        self.register.ui.pushButton_Create.clicked.connect(self.create_account)
    

    #customer representive functions
    def ban_customer(self):
        if not self.selectedEmail:
            QMessageBox.warning(self.customer_representive, "WARNING", "Please select a customer.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.customer_id
                FROM customers c
                JOIN users u ON c.user_id = u.user_id
                WHERE u.email = ?
            """, (self.selectedEmail,))

            result = cursor.fetchone()
            if not result:
                print("Customer NOT FOUND:", self.selectedEmail)
                return

            customer_id = result[0]

            cursor.execute(
                "SELECT 1 FROM banned_customers WHERE customer_id = ?",
                (customer_id,)
            )
            if cursor.fetchone():
                print("Customer already banned:", customer_id)
                return

            cursor.execute(
                "INSERT INTO banned_customers (customer_id) VALUES (?)",
                (customer_id,)
            )

            conn.commit()
            print("Customer successfully banned:", customer_id)

        except Exception as e:
            print("BAN CUSTOMER ERROR:", e)

        finally:
            try:
                conn.close()
            except:
                pass


    def load_customers(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    u.first_name,
                    u.last_name,
                    u.email,
                    u.phone,
                    m.complain_topic,
                    c.customer_id
                FROM messages m
                JOIN customers c ON m.customer_id = c.customer_id
                JOIN users u ON c.user_id = u.user_id
            """)

            rows = cursor.fetchall()
            self.customer_representive.ui.tbl_customer.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                for col_idx in range(5):  
                    self.customer_representive.ui.tbl_customer.setItem(
                        row_idx, col_idx, QTableWidgetItem(str(row_data[col_idx]))
                    )

            conn.close()

        except Exception as e:
            print("There is no DB connect, MOCK data is been using:", e)
            self.load_customers_mock()


    def load_customers_mock(self):
        self.customer_representive.ui.tbl_customer.setRowCount(len(MESSAGES))

        for row_idx, msg in enumerate(MESSAGES):
            self.customer_representive.ui.tbl_customer.setItem(row_idx, 0, QTableWidgetItem("Test"))
            self.customer_representive.ui.tbl_customer.setItem(row_idx, 1, QTableWidgetItem("User"))
            self.customer_representive.ui.tbl_customer.setItem(row_idx, 2, QTableWidgetItem(msg["email"]))
            self.customer_representive.ui.tbl_customer.setItem(row_idx, 3, QTableWidgetItem("555-0000"))
            self.customer_representive.ui.tbl_customer.setItem(row_idx, 4, QTableWidgetItem(msg["complaint"]))



    def on_row_clicked(self, row, column):
        email_item = self.customer_representive.ui.tbl_customer.item(row, 2)
        if not email_item:
            return

        self.selectedEmail = email_item.text()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT m.complain_topic
                FROM messages m
                JOIN customers c ON m.customer_id = c.customer_id
                JOIN users u ON c.user_id = u.user_id
                WHERE u.email = ?
            """, (self.selectedEmail,))

            result = cursor.fetchone()
            conn.close()

            if result:
                self.customer_representive.ui.txt_viewComplaint.setPlainText(result[0])
                return

        except Exception as e:
            print("DB not available, using mock complaint")

        self.customer_representive.ui.txt_viewComplaint.setPlainText("Complaint not available.")

    def send_email(self, to_email, subject, body):
        company_email = "bdudukeskin@gmail.com"
        app_password = "zyyj zkkz uckw fekj"
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = company_email
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(company_email, app_password)
            smtp.send_message(msg)

    def send_feedback(self):
        if not self.selectedEmail:
            QMessageBox.warning(self.customer_representive, "WARNING", "You must select a customer first.")
            return

        feedback_text = self.customer_representive.ui.txt_writeFeedback.toPlainText().strip()
        if not feedback_text:
            QMessageBox.warning(self.customer_representive, "WARNING", "Feedback can not be empty.")
            return

        for msg in MESSAGES:
            if msg["email"] == self.selectedEmail:
                msg["feedback"] = feedback_text
                break

        try:
            self.send_email(
                to_email=self.selectedEmail,
                subject="Customer Support Feedback",
                body=feedback_text
            )
            QMessageBox.information(
                self.customer_representive,
                "SUCCESS",
                f"Feedback sent to {self.selectedEmail}"
            )
        except Exception as e:
            QMessageBox.critical(self.customer_representive, "MAIL ERROR", str(e))
    
    # customer representive functions end


    # DBA panel functions start ---

    def show_product(self):
        self.product.show()

    def show_salelog(self):
        self.load_sales_logs()   
        self.salelog.show()

    def load_products(self):
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    p.product_id,
                    p.product_name,
                    v.vendor_name,
                    p.quantity,
                    p.category,
                    p.unit_price,
                    p.total_price
                FROM products p
                JOIN vendors v ON v.vendor_id = p.vendor_id
                ORDER BY p.product_id DESC
            """)
            rows = cur.fetchall()

            self.product.tableWidget.setRowCount(0)

            for r, row in enumerate(rows):
                self.product.tableWidget.insertRow(r)
                for c, val in enumerate(row):
                    item = QTableWidgetItem("" if val is None else str(val))
                    self.product.tableWidget.setItem(r, c, item)

        except Exception as e:
            QMessageBox.critical(self.product, "DB Error", str(e))

    
    def on_table_selection_changed(self):
        items = self.product.tableWidget.selectedItems()
        if not items:
            return

        row = self.product.tableWidget.currentRow()

        self.selected_product_id = int(self.product.tableWidget.item(row, 0).text())
        self.product.productIdInput.setText(self.product.tableWidget.item(row, 0).text())
        self.product.productNameInput.setText(self.product.tableWidget.item(row, 1).text())

        vendor_id = self.product.tableWidget.item(row, 2).text()
        qty = self.product.tableWidget.item(row, 3).text()
        category = self.product.tableWidget.item(row, 4).text()
        unit_price = self.product.tableWidget.item(row, 5).text()
        total_price = self.product.tableWidget.item(row, 6).text()

        self.product.quantityInput.setText(qty)
        self.product.unitPriceInput.setText(unit_price)
        self.product.totalPriceInput.setText(total_price)
        idx = self.product.vendorCombo.findText(vendor_id)
        if idx != -1:
            self.product.vendorCombo.setCurrentIndex(idx)

        idx2 = self.product.categorycombo.findText(category)
        if idx2 != -1:
            self.product.categorycombo.setCurrentIndex(idx2)

    def add_product(self):
        try:
            name = self.product.productNameInput.text().strip()
            vendor_id = self.product.vendorCombo.currentData()
            category = self.product.categorycombo.currentText()

            qty_text = self.product.quantityInput.text().strip()
            price_text = self.product.unitPriceInput.text().strip()

            if not name:
                QMessageBox.warning(self.product, "Invalid", "Prodcut name cant be empty.")
                return
            if vendor_id is None:
                QMessageBox.warning(self.product, "Invalid", "You should chose vendor.")
                return
            if qty_text == "" or price_text == "":
                QMessageBox.warning(self.product, "Invalid", "Quantity and Unit Price cant be empty.")
                return

            quantity = int(qty_text)
            unit_price = int(price_text)

            if quantity < 0:
                QMessageBox.warning(self.product, "Invalid Quantity", "Quantity cant be smaller than 0.")
                return
            if unit_price < 0:
                QMessageBox.warning(self.product, "Invalid Price", "Unit Price cant be smaller than 0.")
                return

            total_price = quantity * unit_price

            cur = conn.cursor()
            cur.execute("""
                INSERT INTO products (product_name, vendor_id, quantity, category, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, vendor_id, quantity, category, unit_price, total_price))
            conn.commit()

            self.load_products()
            self.clear_form()

        except ValueError:
            QMessageBox.warning(self.product, "Invalid", "Quantity and Unit must be numerical.")
        except Exception as e:
            QMessageBox.critical(self.product, "Error", str(e))


    def update_product(self):
        if self.selected_product_id is None:
            QMessageBox.information(self.product, "Info", "Select product from table first.")
            return

        try:
            name = self.product.productNameInput.text().strip()
            if not name:
                QMessageBox.warning(self.product, "Warning", "Product name can not be blank.")
                return

            vendor_id = self.product.vendorCombo.currentData()
            if vendor_id is None:
                QMessageBox.warning(self.product, "Warning", "Choose vendor.")
                return

            qty_text = self.product.quantityInput.text().strip()
            price_text = self.product.unitPriceInput.text().strip()

            if qty_text == "" or price_text == "":
                QMessageBox.warning(self.product, "Warning", "Quantity and Unit Price can not be empty.")
                return

            quantity = int(qty_text)
            unit_price = int(price_text)

            if quantity < 0:
                QMessageBox.warning(self.product, "Invalid Quantity", "Quantity must be bigger than 0.")
                return
            if unit_price < 0:
                QMessageBox.warning(self.product, "Invalid Price", "Unit Price must be smaller than 0.")
                return

            total_price = quantity * unit_price
            category = self.product.categorycombo.currentText()

            cur = conn.cursor()
            cur.execute("""
                UPDATE products
                SET product_name=?, vendor_id=?, quantity=?, category=?, unit_price=?, total_price=?
                WHERE product_id=?
            """, (name, vendor_id, quantity, category, unit_price, total_price, self.selected_product_id))

            conn.commit()
            self.load_products()
            QMessageBox.information(self.product, "Success", "Product Updated!")

        except ValueError:
            QMessageBox.warning(self.product, "Warning", "Quantity and Unit Price only can be numerical.")
        except Exception as e:
            QMessageBox.critical(self.product, "Error", str(e))



    def delete_product(self):
        """DELETE"""
        if self.selected_product_id is None:
            QMessageBox.information(self.product, "Info", "Please select a product from table first.")
            return

        ans = QMessageBox.question(self.product, "Confirm", "Do you want to delete?")
        if ans != QMessageBox.StandardButton.Yes:
            return

        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM products WHERE product_id=?", (self.selected_product_id,))
            conn.commit()

            self.load_products()
            self.clear_form()

        except Exception as e:
            QMessageBox.critical(self.product, "Error", str(e))

    def clear_form(self):
        self.selected_product_id = None
        self.product.productIdInput.clear()
        self.product.productNameInput.clear()
        self.product.quantityInput.clear()
        self.product.unitPriceInput.clear()
        self.product.totalPriceInput.clear()

    def load_vendors(self):
        cur = conn.cursor()
        cur.execute("SELECT vendor_id, vendor_name FROM vendors ORDER BY vendor_name")
        self.product.vendorCombo.clear()

        for vendor_id, vendor_name in cur.fetchall():
            self.product.vendorCombo.addItem(vendor_name, vendor_id)  


    def load_sales_logs(self):
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    s.sales_log_id,
                    o.order_id,
                    p.product_name,
                    o.customer_id,
                    o.quantity,
                    o.total_price,
                    o.order_status,
                    o.created_at
                FROM sales_logs s
                INNER JOIN orders o   ON o.order_id = s.order_id
                INNER JOIN products p ON p.product_id = o.product_id
                ORDER BY s.sales_log_id DESC
            """)
            rows = cur.fetchall()

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                "Sales Log ID",
                "Order ID",
                "Product",
                "Customer ID",
                "Quantity",
                "Total Price",
                "Order Status",
                "Created At"
            ])

            for row in rows:
                model.appendRow([QStandardItem("" if x is None else str(x)) for x in row])

            self.salelog.set_model(model)

        except Exception as e:
            QMessageBox.critical(self.salelog, "DB Error", str(e))



    # Couier panel functions start -----
    def load_orders(self):
        sql = """
        SELECT
            o.order_id,
            o.customer_id,
            o.address_id,
            o.vendor_id,
            v.vendor_name,
            o.product_id,
            p.product_name,
            o.order_status,
            o.quantity,
            o.total_price,
            o.created_at
        FROM orders o
        LEFT JOIN vendors  v ON v.vendor_id  = o.vendor_id
        LEFT JOIN products p ON p.product_id = o.product_id
        ORDER BY o.order_id DESC
        """

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            headers = [col[0] for col in cur.description]
        except Exception as e:
            QMessageBox.critical(self.courier, "DB Error", str(e))
            return
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass


        self.model.clear()
        self.model.setColumnCount(len(headers))
        self.model.setHorizontalHeaderLabels(headers)

        for r in rows:
            items = []
            for val in r:
                it = QStandardItem("" if val is None else str(val))
                it.setEditable(False)
                items.append(it)
            self.model.appendRow(items)

        self.courier.ui.tblOrders.resizeColumnsToContents()

    def get_selected_order_id(self):
        index = self.courier.ui.tblOrders.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self.courier, "Warning", "Please choose an order.")
            return None

        row = index.row()
        item = self.model.item(row, 0)  
        if not item:
            return None

        try:
            return int(item.text())
        except ValueError:
            return None

    def update_order_status(self, order_id, status):
        sql = "UPDATE orders SET order_status=? WHERE order_id=?"

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (status, order_id))
            conn.commit()
            return True
        except Exception as e:
            QMessageBox.critical(self.courier, "DB Error", str(e))
            return False
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass

    def take_selected_order(self):
        order_id = self.get_selected_order_id()
        if not order_id:
            return

        if self.update_order_status(order_id, "shipped"):
            QMessageBox.information(self.courier, "Succsesfull", "Order was taken succsesful.")
            self.load_orders()

    def deliver_selected_order(self):
        order_id = self.get_selected_order_id()
        if not order_id:
            return

        if self.update_order_status(order_id, "delivered"):
            QMessageBox.information(self.courier, "Succsessful", "Delivered.")
            self.load_orders()

    
    # Couier panel functions end ------

    #Contact panel functions
    def list_messages(self):
        sql = "SELECT complain_topic, feedback FROM MESSAGES WHERE customer_id = ?"
        try:
            cursor.execute(sql, (self.general_id,))
            
        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self.contact, "Database Error", str(e))
            return

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description] 

        model = QStandardItemModel()
        model.setColumnCount(len(columns))
        model.setHorizontalHeaderLabels(columns)

        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                item = QStandardItem("" if value is None else str(value))
                model.setItem(r, c, item)

        self.contact.ui.tableView.setModel(model)
        self.contact.ui.tableView.resizeColumnsToContents()
    
    def send_complaint_message(self):
        sql = """
        INSERT INTO MESSAGES (customer_id, complain_topic, feedback, created_at)
        VALUES (?, ?, ?, ?)
        """
        time = datetime.now()
        topic = self.contact.ui.lineEdit_Topic.text()
        feedback = self.contact.ui.plainTextEdit_Message.toPlainText()
        data = (self.general_id,topic,feedback,time)

        try:
            cursor.execute(sql, data)
            conn.commit()

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self.contact, "Database Error", str(e))


    def back_to_customer(self):
        self.contact.hide()
        self.customer.show()
        

    #Customer panel functions
    def back_to_login(self):
        self.customer.close()
        self.login.show()
    def get_selected_value_by_column_name(self, column_name: str, table_name: str):
        view_name = f"tableView_{table_name}"
        view = getattr(self.customer.ui, view_name, None)

        if view is None:
            return None

        model = view.model()
        selection_model = view.selectionModel()

        if model is None or not selection_model.hasSelection():
            return None

        row = selection_model.selectedRows()[0].row()

        for col in range(model.columnCount()):
            if model.headerData(col, Qt.Horizontal) == column_name:
                return model.index(row, col).data()

        return None
    def list_orders(self):
        sql = """
        SELECT * FROM orders WHERE customer_id = ?
            """
        try:
            print(self.general_id)
            cursor.execute(sql, (self.general_id,))

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self.customer, "Database Error", str(e))
            return
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description] 

        model = QStandardItemModel()
        model.setColumnCount(len(columns))
        model.setHorizontalHeaderLabels(columns)

        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                model.setItem(r, c, QStandardItem("" if value is None else str(value)))

        self.customer.ui.tableView_Order.setModel(model)
        self.customer.ui.tableView_Order.resizeColumnsToContents()

    def list_cities(self):
        sql = "SELECT city_id, city_name FROM cities"
        try:
            cursor.execute(sql)

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self.customer, "Database Error", str(e))
            return

        combo = self.customer.ui.comboBox_City
        combo.clear()

        for city_id, city_name in cursor.fetchall():
            combo.addItem(city_name, city_id)
    def list_districts(self):
        sql = "SELECT district_id, district_name FROM districts WHERE city_id = ?"
        try:
            city_id = self.customer.ui.comboBox_City.currentData()
            cursor.execute(sql,(city_id,))

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self.customer, "Database Error", str(e))
            return

        combo = self.customer.ui.comboBox_District
        combo.clear()

        for district_id, district_name in cursor.fetchall():
            combo.addItem(district_name, district_id)
    def list_address_types(self):
        combo = self.customer.ui.comboBox_Type
        combo.addItems(["House", "Workplace"])
    def list_products(self):
        sql = "SELECT * FROM PRODUCTS"
        try:
            cursor.execute(sql)

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self.customer, "Database Error", str(e))
            return

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description] 

        model = QStandardItemModel()
        model.setColumnCount(len(columns))
        model.setHorizontalHeaderLabels(columns)

        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                item = QStandardItem("" if value is None else str(value))
                model.setItem(r, c, item)

        self.customer.ui.tableView_Product.setModel(model)
        self.customer.ui.tableView_Product.resizeColumnsToContents()
    def list_addresses(self):
        sql = """
        SELECT *
        FROM address a
        JOIN cities c    ON c.city_id = a.city_id
        JOIN districts d ON d.district_id = a.district_id
        WHERE a.customer_id = ?
        ORDER BY a.address_id DESC;
            """
        try:
            print(self.general_id)
            cursor.execute(sql, (self.general_id,))

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self.customer, "Database Error", str(e))
            return
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]  

        model = QStandardItemModel()
        model.setColumnCount(len(columns))
        model.setHorizontalHeaderLabels(columns)

        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                model.setItem(r, c, QStandardItem("" if value is None else str(value)))

        self.customer.ui.tableView_Address.setModel(model)
        self.customer.ui.tableView_Address.resizeColumnsToContents()
    def refresh_tables(self):
        self.list_products()
        self.list_addresses()
        self.list_cities()
        self.list_districts()
        self.list_orders()
    def add_address(self):
        sql = """
            INSERT INTO ADDRESS (customer_id, address_type, city_id, district_id, address_description, postal_code)
            VALUES (?, ?, ?, ?, ?, ?)
            """
        address_type = self.customer.ui.comboBox_Type.currentText()
        city_id = self.customer.ui.comboBox_City.currentData()
        district_id = self.customer.ui.comboBox_District.currentData()
        address_description = self.customer.ui.textEdit_Address.toPlainText()
        postal_code = self.customer.ui.lineEdit_PostalCode.text()
        data = (self.general_id, address_type, city_id, district_id, address_description, postal_code)
        try:
            cursor.execute(sql, data)
            conn.commit()

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self.customer, "Database Error", str(e))
            return

    def give_order(self):
        try:
            product_id = self.get_selected_value_by_column_name("product_id", "Product")
            address_id = self.get_selected_value_by_column_name("address_id", "Address")

            if product_id is None or address_id is None:
                QMessageBox.warning(self.customer, "Warning", "Please select both item and address.")
                return

            qty_text = self.customer.ui.lineEdit_Quantity.text().strip()
            if qty_text == "":
                QMessageBox.warning(self.customer, "Warning", "Quantity cant be empty.")
                return

            quantity = int(qty_text)
            if quantity <= 0:
                QMessageBox.warning(self.customer, "Warning", "Quantity must be bigger than 0.")
                return

            cursor.execute("SELECT quantity, unit_price FROM products WHERE product_id = ?", (product_id,))
            row = cursor.fetchone()
            if row is None:
                QMessageBox.warning(self.customer, "Warning", "Item could not found.")
                return

            available_quantity = int(row[0])
            unit_price = int(row[1])

            if quantity > available_quantity:
                QMessageBox.critical(self.customer, "Database Error", "Requested quantity is not present in stock")
                return

            total_price = quantity * unit_price
            order_status = "Order Placed"
            time = datetime.now()

            cursor.execute("""
                UPDATE products
                SET quantity = quantity - ?
                WHERE product_id = ?;
            """, (quantity, product_id))

            cursor.execute("""
                INSERT INTO orders (customer_id, product_id, address_id, order_status, quantity, total_price, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (self.general_id, product_id, address_id, order_status, quantity, total_price, time))

            conn.commit()

            QMessageBox.information(self.customer, "Success", "Order placed and stock updated!")
            self.refresh_tables()  

        except ValueError:
            QMessageBox.warning(self.customer, "Warning", "Quantity must be numerical.")
            conn.rollback()
        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self.customer, "Database Error", str(e))

            
    def show_contact(self):
        self.customer.hide()
        self.contact.show()
        self.list_messages()
    #Login panel functions
    def find_general_id(self,user_id,role_name):
        sql = f"SELECT {role_name}_id FROM {role_name + 's'} WHERE user_id = ?"
        try:
            cursor.execute(sql, (user_id,))
            
        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self.login, "Database Error", str(e))
            return
        
        row2 = cursor.fetchone()
        print(row2)
        if row2:
            self.general_id = row2[0] 
        else:
            pass

    def show_register(self):
        self.login.hide()
        self.register.show()

    def show_customer(self):
        self.login.hide()
        self.customer.show()
        self.list_products()
        self.list_addresses()
        self.list_cities()
        self.list_address_types()
        

    def show_customer_representive(self):
        self.login.hide()
        self.customer_representive.show()
        self.list_products()
        self.list_addresses()
        self.list_cities()
        self.list_districts()

    def show_courier(self):
        self.login.hide()
        self.courier.show()
        self.load_orders()

    def show_product(self):
        self.login.hide()
        self.product.show()
        
    def show_salelog(self):
        self.login.hide()
        self.salelog.show()
        self.load_sales_logs()   
        self.list_products()
        self.list_addresses()
        self.list_cities()
        self.list_districts()

    
    def sign_in(self):
        login_str = self.login.ui.lineEdit_Login.text()
        password = self.login.ui.lineEdit_Password.text()
        data = (login_str, password)
        if password == "" or login_str == "":
            self.login.ui.label_Msg.setText("Blank areas exist.")
            return
        email = "@" in login_str
        if email:
            sql = """
            SELECT *
            FROM users
            WHERE email = ? AND password = ?
            """
            try:
                cursor.execute(sql, data)

            except pyodbc.Error as e:
                conn.rollback()
                QMessageBox.critical(self.login, "Database Error", str(e))
                return
        else:
            sql = """
            SELECT *
            FROM users
            WHERE username = ? AND password = ?
            """
            try:
                cursor.execute(sql, data)

            except pyodbc.Error as e:
                conn.rollback()
                QMessageBox.critical(self.login, "Database Error", str(e))
                return
        row = cursor.fetchone()
        if row:

            role_id = row.role_id

            if role_id == 1:
                cursor.execute("""
                    SELECT 1
                    FROM banned_customers bc
                    JOIN customers c ON c.customer_id = bc.customer_id
                    WHERE c.user_id = ?
                """, (row.user_id,))

                if cursor.fetchone():
                    QMessageBox.critical(
                        self.login,
                        "Access Denied",
                        "Your account has been banned. Please contact support."
                    )
                    return

            if role_id == 1:
                self.show_customer()
                self.find_general_id(row.user_id,'customer')
            elif role_id == 2:
                self.show_customer_representive()
            elif role_id == 3:
                self.show_courier() 
            elif role_id == 4:
                self.show_product() 
            elif role_id == 5:
                self.show_salelog()
        else:
            self.login.ui.label_Msg.setText("Invalid credentials.")
    

    # Register panel functions    
    def is_valid_password(self, pw: str) -> bool:
        return self.pattern.fullmatch(pw) is not None
    def show_login(self):
        self.register.hide()
        self.login.show()
    def create_account(self):
        fname = self.register.ui.lineEdit_Fname.text()
        lname = self.register.ui.lineEdit_Lname.text()
        username = self.register.ui.lineEdit_Username.text()
        email = self.register.ui.lineEdit_Email.text()
        password = self.register.ui.lineEdit_Password.text()
        phone = self.register.ui.lineEdit_Phone.text()

        if not all([fname, lname, username, email, password, phone]):
            self.register.ui.label_msg.setText("Blank areas exist.")
            return

        if "@" not in email:
            self.register.ui.label_msg.setText("Invalid e-mail address.")
            return

        if not self.is_valid_password(password):
            self.register.ui.label_msg.setText("Password must be at least 3 characters long.")
            return

        time = datetime.now()

        try:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, role_id, created_at, username, email, password, phone)
                OUTPUT INSERTED.user_id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (fname, lname, 1, time, username, email, password, phone))

            row = cursor.fetchone()
            if not row:
                raise Exception("User created but user_id could not be retrieved.")

            new_user_id = int(row[0])

            cursor.execute(
                "INSERT INTO customers (user_id) VALUES (?);",
                (new_user_id,)
            )

            conn.commit()

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self.register, "Database Error", str(e))
            return

        QMessageBox.information(self.register, "Success", "Account created successfully.")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    controller = Controller()
    controller.login.show()     
    sys.exit(app.exec_())












