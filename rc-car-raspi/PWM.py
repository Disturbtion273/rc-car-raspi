class PWM:
    I2C_ADDR = 0x14  # I2C-Adresse des Robot HAT V4 MCU

    PWM_CHANNEL = 0   # P0 = Kanal 0
    TIMER_INDEX = 0   # P0-P3 = Timer 0
    PWM_RESOLUTION = 4095  # 12-bit
    PWM_FREQ = 50  # Servo Frequenz in Hz (50Hz)

    REG_CHN_BASE = 0x20
    REG_PSC_BASE = 0x40
    REG_ARR_BASE = 0x44
    
    def __init__(self, i2c):
        self.I2C = i2c
        self.TimerRegister = 0x44
        self.PrescalerRegister = 0x40
        self.Setup()

    def Setup(self, frequency=50):
        TIMER_INDEX = 0
        REG_PSC_BASE= 0x40
        REG_ARR_BASE = 0x44
        PWM_RESOLUTION = 4095
        PWM_FREQ = 50 
        self.I2C.WriteWordData(self.TimerRegister, 4095)
        prescaler = int(72000000 / (4095 + 1) / frequency) - 1
        self.I2C.WriteWordData(self.PrescalerRegister, prescaler)

        # Periode auf 4095 setzen
        self.I2C.write_register(REG_ARR_BASE + TIMER_INDEX, PWM_RESOLUTION)
        # Prescaler berechnen und setzen
        prescaler = int(72000000 / ((PWM_RESOLUTION + 1) * PWM_FREQ)) - 1
        self.I2C.write_register(REG_PSC_BASE + TIMER_INDEX, prescaler)
        print(f"PWM Setup: Prescaler={prescaler}, Period={PWM_RESOLUTION}")


    def SetMotorPwm(self, channel, speed):
        value = max(0, min(speed, 4095))
        # Tauscht MSB mit LSB für die I2C Kommunikation
        msb = (value >> 8) & 0xFF
        lsb = value & 0xFF
        swapped = (lsb << 8) + msb

        PWM_FREQ = 50 
        PWM_CHANNEL = 0
        self.I2C.WriteWordData(channel, swapped)

    def SetAngleToPulse(self,  min_us=500, max_us=2500):
        PWM_RESOLUTION = 4095
        pulse_us = min_us + (angle / 180.0) * (max_us - min_us)
        period_us = 1e6 / PWM_FREQ
        duty_cycle = pulse_us / period_us
        return int(duty_cycle * PWM_RESOLUTION)