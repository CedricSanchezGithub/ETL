#!/bin/bash

# 📦 Répertoire source sur le PC local
SRC="/home/cedric/PycharmProjects/MSPR_ETL/ETL/ressource/image/train/"

# 🎯 Répertoire cible sur le Raspberry Pi
DEST="pi@192.168.1.50:/home/pi/ETL/ETL/ressource/image/train/"

# 🔁 Synchronisation avec rsync (plus sûr et redémarrable)
echo "🔄 Transfert en cours des dossiers d'images..."
rsync -avz "$SRC" "$DEST"

echo "✅ Transfert terminé."
