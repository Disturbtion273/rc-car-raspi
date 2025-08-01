class PWM:
    def __init__(self, i2c):
        self.I2C = i2c
        self.TimerRegister = 0x44
        self.PrescalerRegister = 0x40

    def InitializeTimer(self, frequency=50):
        self.I2C.WriteWordData(self.TimerRegister, 4095)
        prescaler = int(72000000 / (4095 + 1) / frequency) - 1
        self.I2C.WriteWordData(self.PrescalerRegister, prescaler)

    def SetMotorPwm(self, channel, speed):
        value = max(0, min(speed, 4095))
        # Tauscht MSB mit LSB für die I2C Kommunikation
        msb = (value >> 8) & 0xFF
        lsb = value & 0xFF
        swapped = (lsb << 8) + msb
        
        self.I2C.WriteWordData(channel, swapped)