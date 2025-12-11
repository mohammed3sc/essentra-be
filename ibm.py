# import ibm_db

# dsn = (
#     "DATABASE=S65D663D;"
#     "HOSTNAME=S65D663D;"
#     "PORT=447;"
#     "PROTOCOL=TCPIP;"
#     "UID=ODBC3CS;"
#     "PWD=esl7ninp29;"
# )

# try:
#     conn = ibm_db.connect(dsn, "", "")
#     print("Connected to database")
#     ibm_db.close(conn)
# except Exception as e:
#     print(f"Failed to connect to database: {e}")

import pyodbc
dsn="S65D663D"
user="ODBC3CS"
password="esl7ninp29"
cnxn = pyodbc.connect(f'DSN={dsn};UID={user};PWD={password}')
cursor = cnxn.cursor()
cursor.execute("SELECT COUNT(*) AS table_count FROM QSYS2.SYSTABLES WHERE TABLE_TYPE = 'T'")
cursor.fetchall()
print(cursor.fetchall())
