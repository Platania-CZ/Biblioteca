from biblioteca import create_app

# Chiamiamo la funzione factory per ottenere l'istanza dell'app
app = create_app()

if __name__ == '__main__':
    # Eseguiamo l'app
    app.run(debug=True)