import smbus2

class I2C:
    # <summary>
    # Initialisiert ein I2C-Objekt mit einer spezifischen Geräteadresse und Busnummer.
    # </summary>
    # <param name="address">Die I2C-Adresse des Zielgeräts. Muss mit der Gerätehardware übereinstimmen.</param>
    # <param name="busNumber">Der I2C-Bus, auf dem kommuniziert wird. In der Regel 1 für Raspberry Pi.</param>
    def __init__(self, address=0x14, busNumber=1):
        self.Address = address
        self.Bus = smbus2.SMBus(busNumber)

    # <summary>
    # Schreibt ein 16-Bit-Wort in ein spezifisches Register des I2C-Geräts.
    # </summary>
    # <param name="register">Das Zielregister im I2C-Gerät.</param>
    # <param name="value">Der zu schreibende 16-Bit-Wert. Muss im gültigen Bereich für das Register liegen.</param>
    def WriteWordData(self, register, value):
        self.Bus.write_word_data(self.Address, register, value)

    # <summary>
    # Schließt die Verbindung zum I2C-Bus, um Ressourcenfreigabe sicherzustellen.
    # </summary>
    def Close(self):
        self.Bus.close()