import RPi.GPIO as GPIO

class Motor:
    def __init__(self, pwm, directionPin, pwmChannel, motorNumber):
        self.PWM = pwm
        self.directionPin = directionPin
        self.pwmChannel = pwmChannel
        self.motorNumber = motorNumber

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.directionPin, GPIO.OUT)

    # <summary>
    # Setzt die Drehrichtung des Motors.
    # </summary>
    # <param name="forward">True für Vorwärts, False für Rückwärts.</param
    def SetDirection(self,forward=True):
        if self.motorNumber == 1:
            GPIO.output(self.directionPin, GPIO.LOW if forward else GPIO.HIGH)
        elif self.motorNumber == 2:
            GPIO.output(self.directionPin, GPIO.HIGH if forward else GPIO.LOW)

    # <summary>
    # Setzt die Geschwindigkeit des Motors in Prozent.
    # </summary>
    # <param name="speedPercent">Die gewünschte Geschwindigkeit in Prozent. -100 - -1 für Rückwärts, 0 für Stop, 1 - 100 für Vorwärts.</param>
    def SetSpeedPercent(self, speedPercent):
        if speedPercent > 0:
            speedPercent = max(15, min(speedPercent, 100))
            self.SetDirection(forward=True)
        elif speedPercent < 0:
            speedPercent = abs(speedPercent)
            self.SetDirection(forward=False)
        else:
            self.Stop()
            return

        # Eine mindest Geschwindgeit von 15% für Vorwärts und -85% für Rückwärts ist nötig,
        # da der Motor sonst nicht richtig anläuft. Es ist auf 2028 begrenzt, da höhere Werte keine Veränderung mehr bewirken.
        speedPercent = max(15, min(speedPercent, 100))
        pwmValue = int((speedPercent / 100.0) * 2028)
        self.PWM.SetMotorPwm(self.pwmChannel, pwmValue)

    # <summary>
    # Stoppt den Motor
    # </summary>
    def Stop(self):
        self.PWM.SetMotorPwm(self.pwmChannel, 0)
