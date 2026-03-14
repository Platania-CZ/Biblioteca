from biblioteca import create_app

# Creiamo l'istanza dell'applicazione chiamando la funzione factory
app = create_app()

if __name__ == '__main__':
    # Avviamo il server di sviluppo
    # debug=True ti permette di vedere gli errori nel browser e riavvia il server a ogni modifica
    app.run(debug=True)