import lgpio
from Data import Data

class Motor:
    def __init__(self, pwm, motorNumber):
        self.PWM = pwm
        self.directionPin = Data.Motors["DirectionLeft"] if motorNumber == 1 else Data.Motors["DirectionRight"]
        self.pwmChannel = Data.Motors["Left"] if motorNumber == 1 else Data.Motors["Right"]
        self.motorNumber = motorNumber
        self.currentDirection = None  
        self.currentSpeed = 0  

        # Use a global chip handle instead of opening multiple times
        if not hasattr(Motor, '_chip_handle'):
            Motor._chip_handle = lgpio.gpiochip_open(0)
            Motor._claimed_pins = set()
        
        self.chip = Motor._chip_handle
        
        # Only claim the pin if it hasn't been claimed already
        if self.directionPin not in Motor._claimed_pins:
            lgpio.gpio_claim_output(self.chip, self.directionPin)
            Motor._claimed_pins.add(self.directionPin)

    def SetDirection(self, forward=True):
        """
        Set the rotation direction of the motor.
        Only updates GPIO if direction actually changes.

        :param forward: True for forward, False for reverse.
        :type forward: bool
        """
        # Only update direction if it has changed
        if self.currentDirection == forward:
            return
            
        if self.motorNumber == 1:
            lgpio.gpio_write(self.chip, self.directionPin, 0 if forward else 1)
        elif self.motorNumber == 2:
            lgpio.gpio_write(self.chip, self.directionPin, 1 if forward else 0)
        
        self.currentDirection = forward

    def SetSpeedPercent(self, speedPercent):
        """
        Set the motor speed as a percentage.
        Only updates PWM if speed actually changes.

        :param speedPercent: Desired speed percentage.
                            -100 to -1 for reverse,
                             0 to stop,
                             1 to 100 for forward.
        :type speedPercent: int
        """
        # Early return if speed hasn't changed
        if self.currentSpeed == speedPercent:
            return
            
        if speedPercent > 0:
            speedPercent = max(15, min(speedPercent, 100))
            self.SetDirection(forward=True)
        elif speedPercent < 0:
            speedPercent = abs(speedPercent)
            self.SetDirection(forward=False)
        else:
            self.Stop()
            return

        # A minimum speed of 15% is required for forward motion
        speedPercent = max(15, min(speedPercent, 100))
        pwmValue = int((speedPercent / 100.0) * 2028)
        
        self.PWM.SetMotorPwm(self.pwmChannel, pwmValue)
        self.currentSpeed = speedPercent if self.currentDirection else -speedPercent

    def Stop(self):
        """
        Stop the motor by setting PWM to 0.
        """
        if self.currentSpeed != 0:  # Only stop if not already stopped
            self.PWM.SetMotorPwm(self.pwmChannel, 0)
            self.currentSpeed = 0

    @classmethod
    def CleanupAll(cls):
        """
        Class method to properly cleanup all GPIO resources.
        Call this when shutting down the application.
        """
        if hasattr(cls, '_chip_handle'):
            lgpio.gpiochip_close(cls._chip_handle)
            delattr(cls, '_chip_handle')
            delattr(cls, '_claimed_pins')