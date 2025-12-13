from PyQt5.QtGui import QRegularExpressionValidator, QStandardItemModel, QStandardItem
from PyQt5.QtCore import QRegularExpression, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox
from login import LoginWindow
from register import RegisterWindow
from customerpanel import CustomerWindow
from contact import ContactWindow
import pyodbc
import re
from datetime import datetime



# Bağlantı bilgileri
server = 'SERVER_ADI'
database = 'DB_ADI'
dbusername = 'KULLANICI'
dbpassword = 'SIFRE'

# MSSQL bağlantısı
conn = pyodbc.connect(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={dbusername};'
    f'PWD={dbpassword}'
)

cursor = conn.cursor()


class Controller:
    def __init__(self):
        self.row = None
        self.general_id = None
        self.pattern = re.compile(r'^(?=.*\d)(?=.*[^\w\s]).{8,}$')
        self.login = LoginWindow()
        self.register = RegisterWindow()
        self.customer = CustomerWindow()
        self.contact = ContactWindow()
        #Contact panel codes
        self.contact.ui.pushButton_Send.clicked.connect(self.send_feedback)
        self.contact.ui.pushButton_Back.clicked.connect(self.back_to_customer)
        #Customer panel codes
        self.customer.ui.pushButton_Refresh.clicked.connect(self.refresh_tables)
        self.customer.ui.pushButton_Order.clicked.connect(self.give_order)
        self.customer.ui.pushButton_Contact.clicked.connect(self.show_contact)
        self.customer.ui.pushButton_Login.clicked.connect(self.back_to_login)
        self.customer.ui.pushButton_Address.clicked.connect(self.add_address)
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
    
    #Contact panel functions
    def list_messages(self):
        sql = "SELECT complain_topic, message FROM MESSAGES WHERE customer_id = ?"
        try:
            cursor.execute(sql, (self.general_id,))
            conn.commit()
            
        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", str(e))
            return

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]  # kolon adları

        model = QStandardItemModel()
        model.setColumnCount(len(columns))
        model.setHorizontalHeaderLabels(columns)

        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                item = QStandardItem("" if value is None else str(value))
                model.setItem(r, c, item)

        self.contact.ui.tableView.setModel(model)
        self.contact.ui.tableView.resizeColumnsToContents()
    
    def send_feedback(self):
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
            QMessageBox.critical(self, "Database Error", str(e))


    def back_to_customer(self):
        self.contact.hide()
        self.customer.show()
        

    #Customer panel functions
    def back_to_login(self):
        self.customer.close()
        self.login.show()
    def get_selected_id(self, id_type):
        view = None
        if id_type == "product_id":
            view = self.customer.ui.tableView_Product
        elif id_type == "address_id":
            view = self.customer.ui.tableView_Address
        model = view.model()
        sel = view.selectionModel()

        if model is None or sel is None:
            return None

        selected_rows = sel.selectedRows()
        if not selected_rows:
            return None  

        row = selected_rows[0].row()


        headers = [model.headerData(i, Qt.Horizontal) for i in range(model.columnCount())]
        try:
            col = headers.index(id_type)
        except ValueError:
            return None 

        requested_id = model.index(row, col).data()
        return requested_id
    def list_cities(self):
        sql = "SELECT city_id, city_name FROM CITIES"
        try:
            cursor.execute(sql)
            conn.commit()

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", str(e))
            return

        combo = self.customer.ui.comboBox_City
        combo.clear()

        for city_id, city_name in cursor.fetchall():
            combo.addItem(city_name, city_id)
    def list_districts(self):
        sql = "SELECT district_id, district_name FROM DISTRICTS"
        try:
            cursor.execute(sql)
            conn.commit()

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", str(e))
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
            conn.commit()

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", str(e))
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
        SELECT
            a.address_type        AS address_type,
            c.city_name           AS city_name,
            d.district_name       AS district_name,
            a.address_description AS address_description,
            a.building_no         AS building_no,
            a.apartment_no        AS apartment_no,
            a.postal_code         AS postal_code
        FROM address a
        JOIN cities c    ON c.city_id = a.city_id
        JOIN districts d ON d.district_id = a.district_id
        WHERE a.customer_id = ?
        ORDER BY a.address_id DESC;
            """
        try:
            cursor.execute(sql, (self.general_id,))
            conn.commit()

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", str(e))
            return
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]  # SELECT alias’ları

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
    def add_address(self):
        sql = """
            INSERT INTO MESSAGES (customer_id, address_type, city_id, district_id, address_description, postal_code)
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
            QMessageBox.critical(self, "Database Error", str(e))
            return
    def give_order(self):
            sql = """
            INSERT INTO MESSAGES (customer_id, product_id, address_id, order_status, quantity, total_price, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            product_id = self.get_selected_id("product_id")
            address_id = self.get_selected_id("address_id")
            order_status = "Order Placed"
            quantity = int(self.customer.ui.lineEdit_Quantity.text())
            sql_price = f"SELECT unit_price FROM PRODUCTS WHERE product_id = ?"
            try:
                cursor.execute(sql, data)
                conn.commit()

            except pyodbc.Error as e:
                conn.rollback()
                QMessageBox.critical(self, "Database Error", str(e))
                return
            row = cursor.fetchone()
            total_price = quantity * row[0]
            time = datetime.now()
            data = (self.general_id, product_id, address_id, order_status, quantity, total_price, time)

            
    def show_contact(self):
        self.customer.hide()
        self.contact.show()
        self.list_messages(self)
    #Login panel functions
    def find_general_id(self,user_id,role_name):
        sql = f"SELECT {role_name}_id FROM {role_name} WHERE user_id = ?"
        try:
            cursor.execute(sql, (self.general_id,))
            conn.commit()
            
        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", str(e))
            return
        
        row2 = cursor.fetchone()
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
                conn.commit()

            except pyodbc.Error as e:
                conn.rollback()
                QMessageBox.critical(self, "Database Error", str(e))
                return
        else:
            sql = """
            SELECT *
            FROM users
            WHERE username = ? AND password = ?
            """
            try:
                cursor.execute(sql, data)
                conn.commit()

            except pyodbc.Error as e:
                conn.rollback()
                QMessageBox.critical(self, "Database Error", str(e))
                return
        row = cursor.fetchone()
        if row:
            role_id = row.role_id
            if role_id == 1:
                self.show_customer()
            elif role_id == 2:
                self.show_customer()
            elif role_id == 3:
                self.show_customer()
            elif role_id == 4:
                self.show_customer()
            elif role_id == 5:
                self.show_customer()
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
        print(fname)
        if fname == "" or lname == "" or username == "" or email == "" or password == "" or phone == "":
            self.register.ui.label_msg.setText("Blank areas exist.")
            return
        if not "@" in email:
            self.register.ui.label_msg.setText("Invalid e-mail address.")
            return
        if not self.is_valid_password(password):
            self.register.ui.label_msg.setText("Password must be at least 8 characters long and contain at least one number and one special character.")
            return
        
        sql = """
        INSERT INTO USER (first_name, last_name, role_id, created_at, username, email, password, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        time = datetime.now()
        data = (fname, lname, 1, time, username, email, password, phone)

        try:
            cursor.execute(sql, data)
            conn.commit()

        except pyodbc.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Database Error", str(e))
            return


        print("Kayıt eklendi.")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    controller = Controller()
    controller.login.show()     #Start with login window
    sys.exit(app.exec_())