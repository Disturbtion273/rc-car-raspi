import time
import threading
from Intersection import Intersection

class LineFollower:
    def __init__(self, driving, grayscaleSensor):
        self.driving = driving
        self.sensor = grayscaleSensor
        self.running = False
        self.thread = None

        # Control parameters
        self.kp = 1.2  # Proportional gain for steering angle
        self.maxSteering = 100
        self.minSteering = 0
        self.maxSpeed = 50
        self.minSpeed = 20

        # Direction preference: "center", "left", or "right"
        self.direction = "center"

    def SetDirection(self, direction):
        print("Set direction to " + direction)
        if direction in ["left", "center", "right"]:
            self.direction = direction
        else:
            raise ValueError("Invalid direction. Use 'left', 'center', or 'right'.")

    def SetSteering(self, value):
        self.driving.SetSteeringPercent(value)

    def ReadLinePosition(self):
        readings = [
            self.sensor.ReadGrayscalePercent(1),  # Left
            self.sensor.ReadGrayscalePercent(2),  # Center
            self.sensor.ReadGrayscalePercent(3)   # Right
        ]

        lineValues = [r / 100.0 for r in readings]
        total = sum(lineValues)

        if total == 0:
            return None  # Line is lost

        position = (lineValues[0] * 0 + lineValues[1] * 50 + lineValues[2] * 100) / total

        # Detect potential fork/split (multiple high readings)
        highThreshold = 0.5  
        leftDetected = lineValues[0] > highThreshold
        rightDetected = lineValues[2] > highThreshold

        if self.direction == "right" and rightDetected and not leftDetected:
            position = 80  # Force bias toward right
        elif self.direction == "left" and leftDetected and not rightDetected:
            position = 20  # Force bias toward left
        elif self.direction == "right":
            position = position * 0.85 + 15  
        elif self.direction == "left":
            position = position * 0.85       

        return max(0, min(100, position))

    def FollowLine(self):
        position = self.ReadLinePosition()
        if position is None:
            self.driving.SetSpeedPercent(self.minSpeed)
            return

        deviation = position - 50  # Deviation: -50 (left) to +50 (right)

        # Amplify deviation for left/right modes
        if self.direction == "left":
            deviation *= 1.8  
        elif self.direction == "right":
            deviation *= 1.8  

        # Proportional steering control
        steeringValue = 50 + self.kp * deviation
        steeringValue = max(self.minSteering, min(self.maxSteering, steeringValue))
        self.driving.SetSteeringPercent(steeringValue)

        # Speed control
        error = abs(deviation)
        speed = self.maxSpeed - (error / 50.0) * (self.maxSpeed - self.minSpeed)
        speed = max(self.minSpeed, min(self.maxSpeed, speed))

        if not Intersection.isWaitedForWebsocketCommand:
            self.driving.SetSpeedPercent(speed)


    def Run(self):
        while self.running:
            self.FollowLine()
            time.sleep(0.02)  # 20 ms delay between control updates

    def Start(self):
        if not self.running:
            self.driving.SetSteeringPercent(50)
            self.running = True
            self.thread = threading.Thread(target=self.Run)
            self.thread.start()

    def Stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.driving.SetSpeedPercent(0)
