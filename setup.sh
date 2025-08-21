#!/bin/bash
set -e  # Script bricht ab, wenn ein Fehler auftritt

VENV_DIR="venv"

echo "🔧 Installiere systemabhängige Pakete..."
sudo apt update
sudo apt install -y libcamera-apps libcamera-dev python3-libcamera python3-pip python3-venv

# Optional: altes venv löschen
if [ -d "$VENV_DIR" ]; then
    echo "🧹 Entferne altes virtuelles Environment..."
    rm -rf $VENV_DIR
fi

echo "🐍 Erstelle virtuelles Environment mit Zugriff auf Systempakete..."
python3 -m venv --system-site-packages $VENV_DIR

echo "⚡ Aktiviere virtuelles Environment..."
source $VENV_DIR/bin/activate

echo "⬆️ Upgrade pip..."
pip install --upgrade pip

echo "📦 Installiere NumPy <2 zuerst..."
pip install "numpy<2"

echo "📦 Installiere restliche Pakete..."
pip install -r requirements.txt

echo "✅ Alle Pakete wurden erfolgreich installiert!"
echo "💡 Um das Environment zu nutzen: source $VENV_DIR/bin/activate"
