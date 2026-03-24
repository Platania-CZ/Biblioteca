from biblioteca.extensions import create_app, db
from models import ClassificazioneDewey, Utente

app = create_app()

# ==========================================
# CREAZIONE TABELLE E POPOLAMENTO
# ==========================================

with app.app_context():
    # 1. Ricrea tutte le tabelle
    db.drop_all()
    db.create_all()
    print("Tabelle create con successo.")

    # 2. Amministratore di default
    if not Utente.query.filter_by(ruolo='amministratore').first():
        admin = Utente(
            username='admin',
            email_address='admin@admin.com',
            ruolo='amministratore'
        )
        admin.password = 'Admin123!'
        db.session.add(admin)
        db.session.commit()
        print("Amministratore creato con successo.")
    else:
        print("Amministratore già presente.")

    # 3. Popolamento Dewey (solo se la tabella è vuota)
    if ClassificazioneDewey.query.count() == 0:
        print("Popolamento classificazione Dewey in corso...")

        dewey_data = {
            '000': [(None, 'Generalità'), ('010', 'Bibliografia'), ('020', 'Biblioteconomia'), ('030', 'Enciclopedie'), ('050', 'Pubblicazioni seriali'), ('060', 'Museologia'), ('070', 'Giornalismo'), ('080', 'Raccolte generali'), ('090', 'Libri rari')],
            '100': [(None, 'Filosofia e psicologia'), ('110', 'Metafisica'), ('120', 'Gnoseologia'), ('130', 'Paranormale'), ('140', 'Scuole filosofiche'), ('150', 'Psicologia'), ('160', 'Logica'), ('170', 'Etica'), ('180', 'Filosofia antica'), ('190', 'Filosofia moderna')],
            '200': [(None, 'Religione'), ('210', 'Filosofia della religione'), ('220', 'Bibbia'), ('230', 'Teologia cristiana'), ('240', 'Morale cristiana'), ('250', 'Ordini religiosi'), ('260', 'Ecclesiologia'), ('270', 'Storia della Chiesa'), ('280', 'Confessioni cristiane'), ('290', 'Altre religioni')],
            '300': [(None, 'Scienze sociali'), ('310', 'Statistica'), ('320', 'Scienza politica'), ('330', 'Economia'), ('340', 'Diritto'), ('350', 'Amministrazione pubblica'), ('360', 'Problemi sociali'), ('370', 'Educazione'), ('380', 'Commercio'), ('390', 'Costumi e folclore')],
            '400': [(None, 'Lingue'), ('410', 'Linguistica'), ('420', 'Inglese'), ('430', 'Lingue germaniche'), ('440', 'Lingue romanze'), ('450', 'Italiano'), ('460', 'Spagnolo e portoghese'), ('470', 'Latino'), ('480', 'Greco classico'), ('490', 'Altre lingue')],
            '500': [(None, 'Scienze pure'), ('510', 'Matematica'), ('520', 'Astronomia'), ('530', 'Fisica'), ('540', 'Chimica'), ('550', 'Scienze della terra'), ('560', 'Paleontologia'), ('570', 'Biologia'), ('580', 'Botanica'), ('590', 'Zoologia')],
            '600': [(None, 'Tecnologia'), ('610', 'Medicina'), ('620', 'Ingegneria'), ('630', 'Agricoltura'), ('640', 'Economia domestica'), ('650', 'Management'), ('660', 'Ingegneria chimica'), ('670', 'Manifattura'), ('680', 'Lavorazioni speciali'), ('690', 'Edilizia')],
            '700': [(None, 'Arti e sport'), ('710', 'Urbanistica'), ('720', 'Architettura'), ('730', 'Scultura'), ('740', 'Disegno'), ('750', 'Pittura'), ('760', 'Grafica'), ('770', 'Fotografia'), ('780', 'Musica'), ('790', 'Spettacolo e sport')],
            '800': [(None, 'Letteratura'), ('810', 'Letteratura americana'), ('820', 'Letteratura inglese'), ('830', 'Letterature germaniche'), ('840', 'Letterature romanze'), ('850', 'Letteratura italiana'), ('860', 'Letterature ispaniche'), ('870', 'Letteratura latina'), ('880', 'Letteratura greca'), ('890', 'Altre letterature')],
            '900': [(None, 'Storia e geografia'), ('910', 'Geografia e viaggi'), ('920', 'Biografia e genealogia'), ('930', 'Storia antica'), ('940', 'Storia d\'Europa'), ('950', 'Storia d\'Asia'), ('960', 'Storia d\'Africa'), ('970', 'Storia del Nord America'), ('980', 'Storia del Sud America'), ('990', 'Storia di altre aree')]
        }

        for principale, sottosezioni in dewey_data.items():
            nome_categoria_principale = next((desc for cod, desc in sottosezioni if cod is None), "Senza categoria")
            for codice_full, desc in sottosezioni:
                if codice_full is None:
                    entry = ClassificazioneDewey(
                        sezione_principale=principale,
                        sottosezione=None,
                        descrizione=desc,
                        descrizione_sottosezione=None
                    )
                else:
                    entry = ClassificazioneDewey(
                        sezione_principale=principale,
                        sottosezione=codice_full[1:],
                        descrizione=nome_categoria_principale,
                        descrizione_sottosezione=desc
                    )
                db.session.add(entry)

        db.session.commit()
        print("Classificazione Dewey popolata con successo!")

    print("Database pronto!")