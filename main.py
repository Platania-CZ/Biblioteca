# - installare MySQL: standalone vs XAMPP
# - installare driver MySQL Connector per Python: pip install mysql-connector-python
'''
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bibliodb"
)

cursor = db.cursor()

sql = "INSERT INTO autori (nome, cognome) VALUES (%s, %s)"
val = [
    ("Dante", "Alighieri"),
    ("Giacomo", "Leopardi"),
    ("Umberto", "Eco"),
    ("Elsa", "Morante"),
    ("Sonia", "Serazzi"),
    ("Saverio", "Strati"),
    ("Sharo", "Gambino"),
    ("Felice", "Mastroianni"),
    ("Victor", "Hugo"),
    ("Gabriel", "Garcia Marquez")
]
cursor.executemany(sql, val)
db.commit()
print(cursor.rowcount, "record inserito.")

'''
