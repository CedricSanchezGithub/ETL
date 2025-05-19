# Pratique pour dev. Ne pas utiliser en prod.
from Backend.scheduler import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
