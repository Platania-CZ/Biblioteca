import mysql.connector
from mysql.connector import Error

def popola_classi_dewey(cursor):
    """
    Popola la tabella classificazione_dewey con le 10 classi principali
    e le relative sottocategorie di secondo livello (decine).
    """
    classi = [
        # 000 Informatica, informazione e opere generali
        ('000', 'Informatica, informazione e opere generali', '000'),
        ('010', 'Bibliografia', '000'), ('020', 'Biblioteconomia e scienza dell’informazione', '000'),
        ('030', 'Opere enciclopediche generali', '000'), ('050', 'Pubblicazioni in serie generali', '000'),
        ('060', 'Organizzazioni e museologia', '000'), ('070', 'Media d’informazione, giornalismo ed editoria', '000'),
        ('080', 'Raccolte generali', '000'), ('090', 'Manoscritti e libri rari', '000'),

        # 100 Filosofia e psicologia
        ('100', 'Filosofia e psicologia', '100'),
        ('110', 'Metafisica', '100'), ('120', 'Epistemologia, causalità, genere umano', '100'),
        ('130', 'Fenomeni paranormali', '100'), ('140', 'Specifiche scuole filosofiche', '100'),
        ('150', 'Psicologia', '100'), ('160', 'Logica', '100'),
        ('170', 'Etica (Filosofia morale)', '100'), ('180', 'Filosofia antica, medievale, orientale', '100'),
        ('190', 'Filosofia moderna occidentale', '100'),

        # 200 Religione
        ('200', 'Religione', '200'),
        ('210', 'Filosofia e teoria della religione', '200'), ('220', 'Bibbia', '200'),
        ('230', 'Cristianesimo e teologia cristiana', '200'), ('240', 'Esperienza, pratica, vita cristiana', '200'),
        ('250', 'Chiesa cristiana locale e ordini religiosi', '200'), ('260', 'Teologia sociale ed ecclesiologia cristiana', '200'),
        ('270', 'Storia del cristianesimo e della chiesa', '200'), ('280', 'Denominazioni e sette cristiane', '200'),
        ('290', 'Altre religioni', '200'),

        # 300 Scienze sociali
        ('300', 'Scienze sociali', '300'),
        ('310', 'Statistica generale', '300'), ('320', 'Scienza politica', '300'),
        ('330', 'Economia', '300'), ('340', 'Diritto', '300'),
        ('350', 'Amministrazione pubblica e arte militare', '300'), ('360', 'Problemi e servizi sociali; associazioni', '300'),
        ('370', 'Educazione', '300'), ('380', 'Commercio, comunicazioni, trasporti', '300'),
        ('390', 'Costumi, galateo, folklore', '300'),

        # 400 Linguaggio
        ('400', 'Linguaggio', '400'),
        ('410', 'Linguistica', '400'), ('420', 'Inglese e inglese antico', '400'),
        ('430', 'Lingue germaniche; tedesco', '400'), ('440', 'Lingue romanze; francese', '400'),
        ('450', 'Italiano, rumeno, reto-romancio', '400'), ('460', 'Lingue spagnola e portoghese', '400'),
        ('470', 'Lingue italiche; latino', '400'), ('480', 'Lingue elleniche; greco classico', '400'),
        ('490', 'Altre lingue', '400'),

        # 500 Scienza
        ('500', 'Scienza', '500'),
        ('510', 'Matematica', '500'), ('520', 'Astronomia e scienze connesse', '500'),
        ('530', 'Fisica', '500'), ('540', 'Chimica e scienze connesse', '500'),
        ('550', 'Scienze della terra', '500'), ('560', 'Paleontologia; paleozoologia', '500'),
        ('570', 'Scienze biologiche', '500'), ('580', 'Scienze botaniche', '500'),
        ('590', 'Scienze zoologiche', '500'),

        # 600 Tecnologia
        ('600', 'Tecnologia', '600'),
        ('610', 'Medicina e salute', '600'), ('620', 'Ingegneria e attività affini', '600'),
        ('630', 'Agricoltura e attività affini', '600'), ('640', 'Economia domestica e vita familiare', '600'),
        ('650', 'Gestione e servizi ausiliari', '600'), ('660', 'Ingegneria chimica', '600'),
        ('670', 'Manifattura', '600'), ('680', 'Manifattura per scopi specifici', '600'),
        ('690', 'Edilizia', '600'),

        # 700 Arti e ricreazione
        ('700', 'Arti e ricreazione', '700'),
        ('710', 'Urbanistica e architettura del paesaggio', '700'), ('720', 'Architettura', '700'),
        ('730', 'Arti plastiche; scultura', '700'), ('740', 'Disegno e arti decorative', '700'),
        ('750', 'Pittura e pitture', '700'), ('760', 'Arti grafiche; incisione e stampe', '700'),
        ('770', 'Fotografia e fotografie', '700'), ('780', 'Musica', '700'),
        ('790', 'Arti ricreative e dello spettacolo', '700'),

        # 800 Letteratura
        ('800', 'Letteratura', '800'),
        ('810', 'Letteratura americana in inglese', '800'), ('820', 'Letterature inglese e inglese antico', '800'),
        ('830', 'Letterature delle lingue germaniche', '800'), ('840', 'Letterature delle lingue romanze', '800'),
        ('850', 'Letterature italiana, rumena, reto-romancia', '800'), ('860', 'Letterature spagnola e portoghese', '800'),
        ('870', 'Letterature delle lingue italiche; latina', '800'), ('880', 'Letterature delle lingue elleniche; greca', '800'),
        ('890', 'Letterature di altre lingue', '800'),

        # 900 Storia e geografia
        ('900', 'Storia e geografia', '900'),
        ('910', 'Geografia e viaggi', '900'), ('920', 'Biografia, genealogia, araldica', '900'),
        ('930', 'Storia del mondo antico fino al 499 ca.', '900'), ('940', 'Storia d’Europa', '900'),
        ('950', 'Storia dell’Asia; Estremo Oriente', '900'), ('960', 'Storia dell’Africa', '900'),
        ('970', 'Storia del Nord America', '900'), ('980', 'Storia del Sud America', '900'),
        ('990', 'Storia di altre aree', '900')
    ]
    
    insert_query = """
        INSERT IGNORE INTO classificazione_dewey (codice, descrizione, sezione_principale)
        VALUES (%s, %s, %s)
    """
    cursor.executemany(insert_query, classi)
    print(f"Tabella Dewey: inseriti {len(classi)} record.")

def setup_database():
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '' # Inserire password se necessaria
    }

    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Creazione Database
        cursor.execute("CREATE DATABASE IF NOT EXISTS bibliodb DEFAULT CHARACTER SET utf8mb4")
        cursor.execute("USE bibliodb")

        # 1. Classificazione Dewey
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classificazione_dewey (
                codice VARCHAR(20) PRIMARY KEY,
                descrizione VARCHAR(255) NOT NULL,
                sezione_principale VARCHAR(20)
            ) ENGINE=InnoDB
        """)

        # 2. Tipi Opere
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tipi_opere (
                id INT AUTO_INCREMENT PRIMARY KEY,
                descrizione VARCHAR(50) NOT NULL UNIQUE
            ) ENGINE=InnoDB
        """)

        # 3. Autori
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS autori (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                cognome VARCHAR(100) NOT NULL,
                nazionalita VARCHAR(50),
                data_nascita DATE
            ) ENGINE=InnoDB
        """)

        # 4. Editori
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS editori (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(150) NOT NULL UNIQUE,
                sede VARCHAR(100)
            ) ENGINE=InnoDB
        """)

        # 5. Opere
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opere (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titolo VARCHAR(255) NOT NULL,
                id_autore INT,
                id_tipo INT,
                codice_dewey VARCHAR(20),
                FOREIGN KEY (id_autore) REFERENCES autori(id) ON DELETE SET NULL,
                FOREIGN KEY (id_tipo) REFERENCES tipi_opere(id),
                FOREIGN KEY (codice_dewey) REFERENCES classificazione_dewey(codice)
            ) ENGINE=InnoDB
        """)

        # 6. Edizioni/Copie
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS copie (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_opera INT,
                id_editore INT,
                isbn VARCHAR(20) UNIQUE,
                anno_pubblicazione INT,
                posizione_scaffale VARCHAR(50),
                stato ENUM('disponibile', 'prestato', 'manutenzione', 'smarrito') DEFAULT 'disponibile',
                FOREIGN KEY (id_opera) REFERENCES opere(id) ON DELETE CASCADE,
                FOREIGN KEY (id_editore) REFERENCES editori(id)
            ) ENGINE=InnoDB
        """)

        # 7. Utenti
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utenti (
                id INT AUTO_INCREMENT PRIMARY KEY,
                codice_fiscale CHAR(16) NOT NULL UNIQUE,
                nome VARCHAR(100) NOT NULL,
                cognome VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE,
                telefono VARCHAR(20),
                data_iscrizione DATE DEFAULT (CURRENT_DATE)
            ) ENGINE=InnoDB
        """)

        # 8. Prestiti
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prestiti (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_copia INT,
                id_utente INT,
                data_inizio DATE NOT NULL,
                data_scadenza DATE NOT NULL,
                data_restituzione_effettiva DATE,
                FOREIGN KEY (id_copia) REFERENCES copie(id),
                FOREIGN KEY (id_utente) REFERENCES utenti(id)
            ) ENGINE=InnoDB
        """)

        # Popolamento Dati Base
        popola_classi_dewey(cursor)
        
        tipi = [('Libro',), ('Rivista',), ('DVD',), ('E-book',), ('CD Audio',)]
        cursor.executemany("INSERT IGNORE INTO tipi_opere (descrizione) VALUES (%s)", tipi)

        connection.commit()
        print("Setup completato con successo. Database 'bibliodb' pronto all'uso.")

    except Error as e:
        print(f"Errore durante il setup: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_database()