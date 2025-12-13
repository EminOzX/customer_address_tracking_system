import sys
import pyodbc
import smtplib
from email.message import EmailMessage
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from ui_customerRepresentative import Ui_customerRepresentative
from mainWindow import RepresentativeWindow  # Giriş yapan kullanıcı penceresi
from connection import get_connection


# --- MOCK messages TABLE ---
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


company_email = "bdudukeskin@gmail.com"
app_password = "zyyj zkkz uckw fekj"



def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = company_email
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(company_email, app_password)
        smtp.send_message(msg)




class Main(RepresentativeWindow):
    def __init__(self, logged_in_user_id):
        super().__init__()
        self.logged_in_user_id = logged_in_user_id  # giriş yapan customer_representive.user_id

        # Table ayarları
        self.ui.tbl_customer.setEditTriggers(self.ui.tbl_customer.NoEditTriggers)
        self.ui.tbl_customer.setSelectionBehavior(self.ui.tbl_customer.SelectRows)
        self.ui.tbl_customer.setSelectionMode(self.ui.tbl_customer.SingleSelection)

        self.selectedEmail = None
        self.ui.tbl_customer.cellClicked.connect(self.on_row_clicked)
        self.ui.btn_sendFeedback.clicked.connect(self.send_feedback)

        self.load_customers()



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
            self.ui.tbl_customer.setRowCount(len(rows))

            for row_idx, row_data in enumerate(rows):
                for col_idx in range(5):  # customer_id UI'da göstermiyoruz
                    self.ui.tbl_customer.setItem(
                        row_idx, col_idx, QTableWidgetItem(str(row_data[col_idx]))
                    )

            conn.close()

        except Exception as e:
            print("DB bağlantısı yok, MOCK data kullanılıyor:", e)
            self.load_customers_mock()


    def load_customers_mock(self):
        self.ui.tbl_customer.setRowCount(len(MESSAGES))

        for row_idx, msg in enumerate(MESSAGES):
            self.ui.tbl_customer.setItem(row_idx, 0, QTableWidgetItem("Test"))
            self.ui.tbl_customer.setItem(row_idx, 1, QTableWidgetItem("User"))
            self.ui.tbl_customer.setItem(row_idx, 2, QTableWidgetItem(msg["email"]))
            self.ui.tbl_customer.setItem(row_idx, 3, QTableWidgetItem("555-0000"))
            self.ui.tbl_customer.setItem(row_idx, 4, QTableWidgetItem(msg["complaint"]))



    def on_row_clicked(self, row, column):
        email_item = self.ui.tbl_customer.item(row, 2)  # Email sütunu
        if not email_item:
            return

        self.selectedEmail = email_item.text()

        # MOCK messages tablosundan complaint bul
        for msg in MESSAGES:
            if msg["email"] == self.selectedEmail:
                self.ui.txt_viewComplaint.setPlainText(msg["complaint"])
                print("Complaint bulundu:", msg["complaint"])
                break



    def send_feedback(self):
        if not self.selectedEmail:
            QMessageBox.warning(self, "WARNING", "You must select a customer first.")
            return

        feedback_text = self.ui.txt_writeFeedback.toPlainText().strip()
        if not feedback_text:
            QMessageBox.warning(self, "WARNING", "Feedback can not be empty.")
            return

        # MOCK DB UPDATE
        for msg in MESSAGES:
            if msg["email"] == self.selectedEmail:
                msg["feedback"] = feedback_text
                break

        try:
            send_email(
                to_email=self.selectedEmail,
                subject="Customer Support Feedback",
                body=feedback_text
            )
            QMessageBox.information(
                self,
                "SUCCESS",
                f"Feedback sent to {self.selectedEmail}"
            )
        except Exception as e:
            QMessageBox.critical(self, "MAIL ERROR", str(e))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    logged_in_user_id = 1  # Giriş yapan customer representative user_id'si
    window = Main(logged_in_user_id)
    window.show()
    sys.exit(app.exec_())
