#!/bin/bash
set -e  # Script bricht ab, wenn ein Fehler auftritt

echo "📦 Installiere Pakete aus requirements.txt ..."
pip install -r requirements.txt

echo "✅ Alle Pakete wurden erfolgreich installiert!"
