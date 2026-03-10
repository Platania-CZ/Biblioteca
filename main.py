# 01 Installazione e introduzione Python/MySQL
# - installare MySQL: standalone vs XAMPP
# - installare driver MySQL Connector per Python: pip install mysql-connector-python
# - import e test
# - creare connessione al database

import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bibliodb"
)

cursor = db.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS libri (id INT AUTO_INCREMENT PRIMARY KEY, titolo VARCHAR(255), autore VARCHAR(255))")
cursor.execute("INSERT INTO libri (titolo, autore) VALUES ('Il Signore degli Anelli', 'J.R.R. Tolkien')")
cursor.execute("INSERT INTO libri (titolo, autore) VALUES ('1984', 'George Orwell')")
cursor.execute("INSERT INTO libri (titolo, autore) VALUES ('Il Nome della Rosa', 'Umberto Eco')")
db.commit()

