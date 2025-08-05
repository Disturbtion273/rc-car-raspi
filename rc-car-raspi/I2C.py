import smbus2

class I2C:

    I2C_ADDR = 0x14  # I2C-Adresse des Robot HAT V4 MCU

    PWM_CHANNEL = 0   # P0 = Kanal 0
    TIMER_INDEX = 0   # P0-P3 = Timer 0
    PWM_RESOLUTION = 4095  # 12-bit
    PWM_FREQ = 50  # Servo Frequenz in Hz (50Hz)

    REG_CHN_BASE = 0x20
    REG_PSC_BASE = 0x40
    REG_ARR_BASE = 0x44
    # <summary>
    # Initialisiert ein I2C-Objekt mit einer spezifischen Geräteadresse und Busnummer.
    # </summary>
    # <param name="address">Die I2C-Adresse des Zielgeräts. Muss mit der Gerätehardware übereinstimmen.</param>
    # <param name="busNumber">Der I2C-Bus, auf dem kommuniziert wird. In der Regel 1 für Raspberry Pi.</param>
    def __init__(self, address=0x14, busNumber=1):
        self.address = address
        self.bus = smbus2.SMBus(busNumber)

    # <summary>
    # Schreibt ein 16-Bit-Wort in ein spezifisches Register des I2C-Geräts.
    # </summary>
    # <param name="register">Das Zielregister im I2C-Gerät.</param>
    # <param name="value">Der zu schreibende 16-Bit-Wert. Muss im gültigen Bereich für das Register liegen.</param>
    def WriteWordData(self, register, value):
        self.bus.write_word_data(self.address, register, value)

    def write_register(self, reg_addr, value):
        """Schreibt einen 16-bit Wert auf 2 Bytes Register"""
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        self.bus.write_i2c_block_data(self.address, reg_addr, [high_byte, low_byte])

    # <summary>
    # Schließt die Verbindung zum I2C-Bus, um Ressourcenfreigabe sicherzustellen.
    # </summary>
    def Close(self):
        self.bus.close()