import lgpio
from Data import Data

class Motor:
    def __init__(self, pwm, motorNumber):
        self.PWM = pwm
        self.directionPin = Data.Motors["DirectionLeft"] if motorNumber == 1 else Data.Motors["DirectionRight"]
        self.pwmChannel = Data.Motors["Left"] if motorNumber == 1 else Data.Motors["Right"]
        self.motorNumber = motorNumber

        self.chip = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(self.chip, self.directionPin)

    def SetDirection(self,forward=True):
        """
        Set the rotation direction of the motor.

        :param forward: True for forward, False for reverse.
        :type forward: bool
        """
        if self.motorNumber == 1:
            lgpio.gpio_write(self.chip, self.directionPin, 0 if forward else 1)
        elif self.motorNumber == 2:
            lgpio.gpio_write(self.chip, self.directionPin, 1 if forward else 0)

    def SetSpeedPercent(self, speedPercent):
        """
        Set the motor speed as a percentage.

        :param speedPercent: Desired speed percentage.
                            -100 to -1 for reverse,
                             0 to stop,
                             1 to 100 for forward.
        :type speedPercent: int
        """
        if speedPercent > 0:
            speedPercent = max(15, min(speedPercent, 100))
            self.SetDirection(forward=True)
        elif speedPercent < 0:
            speedPercent = abs(speedPercent)
            self.SetDirection(forward=False)
        else:
            self.Stop()
            return

        # A minimum speed of 15% is required for forward motion, and 85% for reverse,
        # as the motor won't run reliably below that.
        speedPercent = max(15, min(speedPercent, 100))
        pwmValue = int((speedPercent / 100.0) * 2028)
        self.PWM.SetMotorPwm(self.pwmChannel, pwmValue)

    def Stop(self):
        """
        Stop the motor by setting PWM to 0.
        """
        self.PWM.SetMotorPwm(self.pwmChannel, 0)

    def Cleanup(self):
        """
        Release GPIO resources.s
        """
        lgpio.gpiochip_close(self.chip)
