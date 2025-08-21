from Data import Data
import time

class Servo:
    def __init__(self, pwm, pin: int):
        self.pwm = pwm
        self.pin = pin
        self.currentAngle = None 
        self.lastUpdate = 0  # Track last update time to prevent rapid updates
        self.minUpdateInterval = 0.02  # Minimum 20ms between updates (50Hz servo frequency)

    def ScaleValue(self, value):
        minValue = Data.ServoRanges[str(self.pin)]["min"]
        maxValue = Data.ServoRanges[str(self.pin)]["max"]
        return minValue + (value/100) * (maxValue - minValue)

    # <param name="angle">Einen Wert zwischen 0 und 100.</param>
    def SetAnglePercent(self, angle: int):
        # Check if angle has actually changed
        if self.currentAngle == angle:
            return
        # Rate limiting to prevent rapid updates that cause jitter
        currentTime = time.time()
        if currentTime - self.lastUpdate < self.minUpdateInterval:
            return

        value = self.ScaleValue(angle)
        self.pwm.SetServoPwm(self.pin, value)

        self.currentAngle = angle
        self.lastUpdate = currentTime

