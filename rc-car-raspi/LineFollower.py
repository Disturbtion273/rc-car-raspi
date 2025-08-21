import time
import threading

class LineFollower:
    def __init__(self, motor1, motor2, grayscale_sensor, steering):
        self.motor1 = motor1
        self.motor2 = motor2
        self.sensor = grayscale_sensor
        self.steering = steering
        self.speed = 50  # Base speed
        self.running = False
        self.thread = None

    def Steering(self, value):
        self.steering.SetAnglePercent(value)

    def ReadLinePosition(self):
        readings = [
            self.sensor.ReadGrayscalePercent(1),
            self.sensor.ReadGrayscalePercent(2),
            self.sensor.ReadGrayscalePercent(3)
        ]

        # Normalize to 0-1
        lineValues = [r / 100.0 for r in readings]  
        # Weighted sum: left=0, middle=50, right=100
        # maps sensor strengths to a single position (0=left, 100=right)
        position = (lineValues[0] * 0 + lineValues[1] * 50 + lineValues[2] * 100)
        total = sum(lineValues)

        if total == 0:
            return None  # no valid line detected, do nothing

        position /= total
        # Clamp to 0–100
        return max(0, min(100, position))

    def FollowLine(self):
        position = self.ReadLinePosition() 
        # Calculate deviation from center (50 = ideal center position)
        deviation = position - 50  

        steeringValue = 50 + deviation
        steeringValue = max(0, min(100, steeringValue))  # Clamp to 0-100
        self.Steering(steeringValue)

        self.motor1.SetSpeedPercent(self.speed)
        self.motor2.SetSpeedPercent(self.speed)

    def Run(self):
        while self.running:
            self.FollowLine()
            time.sleep(0.02)  

    def Start(self):
        """
        Starts line following 
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.Run)
            self.thread.start()

    def Stop(self):
        """
        Stops line following 
        """
        self.running = False
        if self.thread:
            self.thread.join()
        self.motor1.SetSpeedPercent(0)
        self.motor2.SetSpeedPercent(0)
