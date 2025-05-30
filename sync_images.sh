#!/bin/bash

# 📦 Répertoire source sur le PC local
#SRC="/home/cedric/PycharmProjects/MSPR_ETL/ETL/ressource/image/train/"
SRC="/home/cedric/PycharmProjects/MSPR_ETL/Backend/static"

# 🎯 Répertoire cible sur le Raspberry Pi
DEST="pi@192.168.1.50:/home/pi/ETL/Backend"

# 🔁 Synchronisation avec rsync (plus sûr et redémarrable)
echo "🔄 Transfert en cours des dossiers d'images..."
rsync -avz "$SRC" "$DEST"

echo "✅ Transfert terminé."
