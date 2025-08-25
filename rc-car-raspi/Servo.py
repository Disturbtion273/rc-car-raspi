import threading
import time
from Data import Data

class Servo:
    def __init__(self, pwm, pin: int):
        self.pwm = pwm
        self.pin = pin
        self.currentAngle = 50  # Start position in the middle 
        self.targetDirection = 0  # -1, 0, 1
        self.targetSpeed = 0      # 0-100
        
        # Thread for continuous movement
        self.running = False
        self.movementThread = None
        
        # Start the movement thread
        self.StartMovementThread()

    def ScaleValue(self, value):
        """Scales a percentage value (0-100%) to the servo range"""
        minValue = Data.ServoRanges[str(self.pin)]["min"]
        maxValue = Data.ServoRanges[str(self.pin)]["max"]
        return minValue + (value / 100) * (maxValue - minValue)

    def SetAnglePercent(self, angle: int):
        """Sets the servo immediately to an absolute angle (0-100%)"""
        angle = max(0, min(100, angle))
        self.currentAngle = angle
        value = self.ScaleValue(angle)
        self.pwm.SetServoPwm(self.pin, value)

    def SetMovement(self, direction: int, speed: int):
        """
        Sets continuous movement.
        
        Args:
            direction: -1 (left/down), 0 (stop), 1 (right/up)
            speed: speed 0-100%
        """
        self.targetDirection = max(-1, min(1, direction))
        self.targetSpeed = max(0, min(100, speed))

    def StartMovementThread(self):
        """Starts the movement thread"""
        if not self.running:
            self.running = True
            self.movementThread = threading.Thread(target=self.MovementLoop, daemon=True)
            self.movementThread.start()

    def StopMovementThread(self):
        """Stops the movement thread"""
        self.running = False
        if self.movementThread:
            self.movementThread.join(timeout=1.0)

    def MovementLoop(self):
        """Thread loop for continuous movement"""
        updateRateHz = 50  # 50 Hz = every 20ms
        updateInterval = 1.0 / updateRateHz
        
        while self.running:
            startTime = time.time()
            
            # Update position if movement is active
            if self.targetDirection != 0 and self.targetSpeed > 0:
                # Calculate step size based on speed
                # speed=100 -> 3% per update, speed=10 -> 0.3% per update
                step = (self.targetSpeed / 100.0) * 3.0
                
                # Calculate new position
                newAngle = self.currentAngle - (step * self.targetDirection)
                newAngle = max(0, min(100, newAngle))
                
                # Move servo only if position changed
                if abs(newAngle - self.currentAngle) > 0.1:
                    self.SetAnglePercent(int(newAngle))
            
            # Timing for next update
            elapsed = time.time() - startTime
            sleepTime = max(0, updateInterval - elapsed)
            time.sleep(sleepTime)

    def Stop(self):
        """Stops the movement"""
        self.targetDirection = 0
        self.targetSpeed = 0

    def GetCurrentAngle(self):
        """Returns the current angle position"""
        return self.currentAngle

    def __del__(self):
        """Cleanup when deleting the object"""
        self.StopMovementThread()
