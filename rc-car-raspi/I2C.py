import smbus2
from Data import Data

class I2C:
    # <summary>
    # Initialisiert ein I2C-Objekt mit einer spezifischen Geräteadresse und Busnummer.
    # </summary>
    # <param name="address">Die I2C-Adresse des Zielgeräts. Muss mit der Gerätehardware übereinstimmen.</param>
    # <param name="busNumber">Der I2C-Bus, auf dem kommuniziert wird. In der Regel 1 für Raspberry Pi.</param>
    def __init__(self, address=Data.I2C["Address"], busNumber=1):
        self.address = address
        self.bus = smbus2.SMBus(busNumber)

    # <summary>
    # Schreibt ein 16-Bit-Wort in ein spezifisches Register des I2C-Geräts.
    # </summary>
    # <param name="register">Das Zielregister im I2C-Gerät.</param>
    # <param name="value">Der zu schreibende 16-Bit-Wert. Muss im gültigen Bereich für das Register liegen.</param>
    def WriteWordData(self, register, value):
        msb = (value >> 8) & 0xFF
        lsb = value & 0xFF
        value = (lsb << 8) + msb
        self.bus.write_word_data(self.address, register, value)

    def WriteRegister(self, register, value):
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        self.bus.write_i2c_block_data(self.address, register, [high_byte, low_byte])

    def ReadADC(self, register):
        self.bus.write_word_data(self.address, register, 0x0000)
        msb = self.bus.read_byte(self.address)
        lsb = self.bus.read_byte(self.address)
        value = (msb << 8) | lsb
        return value


    # <summary>
    # Schließt die Verbindung zum I2C-Bus, um Ressourcenfreigabe sicherzustellen.
    # </summary>
    def Close(self):
        self.bus.close()