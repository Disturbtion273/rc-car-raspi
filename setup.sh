#!/bin/bash
set -e  # Script bricht ab, wenn ein Fehler auftritt
 
VENV_DIR="venv"

echo "🔧 Installiere systemabhängige Pakete..."
sudo apt update

sudo apt install -y \
    libcamera-apps libcamera-dev python3-libcamera python3-pip python3-venv git \
    ffmpeg libportaudio2  # ffmpeg für pydub/mp3->wav, portaudio für sounddevice
 
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
 
echo "📦 Installiere Abhängigkeiten aus requirements.txt..."
pip install -r requirements.txt

echo "Setup i2s..."
sudo bash ./i2samp.sh
 
echo "✅ Setup abgeschlossen. Aktiviere dein Environment mit:"
echo "   source $VENV_DIR/bin/activate"


