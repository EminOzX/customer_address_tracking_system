#bu kod localhost : USER_TRACKING_SYSTEM isimli database'e bağlantı gerçekleştirir.

import pyodbc

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=USER_TRACKING_SYSTEM;"
    "Trusted_Connection=yes;"
)

def get_connection():
    return pyodbc.connect(CONN_STR)
