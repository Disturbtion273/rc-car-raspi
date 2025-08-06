from Data import Data

class Servo:
    def __init__(self, pwm, pin: int):
        self.pwm = pwm
        self.pin = pin

    def ScaleValue(self, value):
        minValue = Data.ServoRanges[str(self.pin)]["min"]
        maxValue = Data.ServoRanges[str(self.pin)]["max"]
        return minValue + (value/100) * (maxValue - minValue)

    # <param name="angle">Einen Wert zwischen 0 und 100.</param>
    def SetAnglePercent(self, angle: int):
        value = self.ScaleValue(angle)
        self.pwm.SetServoPwm(self.pin, value)
