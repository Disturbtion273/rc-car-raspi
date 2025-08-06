from I2C import I2C
from Data import Data

class Servo:
    def __init__(self, i2c: I2C, pin: int):
        self.i2c = i2c
        self.pin = pin

    def AngleToPulse(self, angle: float, min_us=500, max_us=2500) -> int:
        pulse_us = min_us + (angle / 180.0) * (max_us - min_us)
        period_us = 1e6 / Data.Pwm["ServoFrequencyHz"]
        duty_cycle = pulse_us / period_us
        return int(duty_cycle * Data.Pwm["Resolution"])

    def ScaleValue(self, value):
        minValue = Data.ServoRanges[str(self.pin)]["min"]
        maxValue = Data.ServoRanges[str(self.pin)]["max"]
        return minValue + (value/100) * (maxValue - minValue)

    # <param name="angle">Einen Wert zwischen 0 und 100.</param>
    def SetAnglePercent(self, angle: int):
        value = self.ScaleValue(angle)
        pulse = self.AngleToPulse(value)
        self.i2c.writeRegister(Data.Registers["ChannelBase"] + self.pin, pulse)
