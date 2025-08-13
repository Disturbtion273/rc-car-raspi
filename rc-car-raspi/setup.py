import subprocess
import sys

# Liste der benötigten Pakete
required_packages = [
    "smbus2",
    "picamera2",
    "RPI.GPIO",
    "websockets",
    "flask",
    "cv2",
]

def install_packages(packages):
    for package in packages:
        print(f"\n🔧 Installing {package} ...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--break-system-packages", package
            ])
        except subprocess.CalledProcessError as e:
            print(f"❌ Fehler beim Installieren von {package}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("📦 Starte Paketinstallation...")
    install_packages(required_packages)
    print("\n✅ Alle Pakete wurden erfolgreich installiert!")
