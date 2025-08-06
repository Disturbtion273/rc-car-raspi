from Data import Data

class PWM:    
    def __init__(self, i2c, frequency=Data.Pwm["ServoFrequencyHz"]):
        self.i2c = i2c
        self.pwmFreq = frequency
        self.Setup()

    def Setup(self, frequency=50):
        self.i2c.WriteWordData(Data.Pwm["Timer"], 4095)
        prescaler = int(72000000 / (4095 + 1) / frequency) - 1
        self.i2c.WriteWordData(Data.Registers["Prescaler"], prescaler)
        self.i2c.writeRegister(Data.Registers["AutoReloadRegister"] + Data.Pwm["Timer"], Data.Pwm["Resolution"])
        prescaler = int(72000000 / ((Data.Pwm["Resolution"] + 1) * Data.Pwm["ServoFrequencyHz"])) - 1
        self.i2c.writeRegister(Data.Registers["Prescaler"] + Data.Pwm["Timer"], prescaler)

    def SetMotorPwm(self, channel, speed):
        value = max(0, min(speed, 4095))
        self.i2c.WriteWordData(channel, value)
