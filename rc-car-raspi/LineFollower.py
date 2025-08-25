import time
import threading

class LineFollower:
    def __init__(self, motor1, motor2, grayscaleSensor, steering):
        self.motor1 = motor1
        self.motor2 = motor2
        self.sensor = grayscaleSensor
        self.steering = steering
        self.running = False
        self.thread = None

        # Control parameters
        self.kp = 1.2  # Proportional gain for steering angle
        self.maxSteering = 100
        self.minSteering = 0
        self.maxSpeed = 65
        self.minSpeed = 20

    def SetSteering(self, value):
        self.steering.SetAnglePercent(value)

    def ReadLinePosition(self):
        # Read grayscale values from the 3 sensors
        readings = [
            self.sensor.ReadGrayscalePercent(1),
            self.sensor.ReadGrayscalePercent(2),
            self.sensor.ReadGrayscalePercent(3)
        ]

        # Normalize to 0–1
        lineValues = [r / 100.0 for r in readings]  
        position = (lineValues[0] * 0 + lineValues[1] * 50 + lineValues[2] * 100)
        total = sum(lineValues)

        if total == 0:
            return None  # No line detected

        position /= total
        return max(0, min(100, position))

    def FollowLine(self):
        position = self.ReadLinePosition()
        if position is None:
            # Line lost – stop or drive straight at minimum speed
            self.motor1.SetSpeedPercent(self.minSpeed)
            self.motor2.SetSpeedPercent(self.minSpeed)
            return

        deviation = position - 50  # -50 (left) to +50 (right)

        # Proportional steering control
        steeringValue = 50 + self.kp * deviation
        steeringValue = max(self.minSteering, min(self.maxSteering, steeringValue))
        self.SetSteering(steeringValue)

        # Speed control – reduce speed with higher deviation
        error = abs(deviation)
        speed = self.maxSpeed - (error / 50.0) * (self.maxSpeed - self.minSpeed)
        speed = max(self.minSpeed, min(self.maxSpeed, speed))

        self.motor1.SetSpeedPercent(speed)
        self.motor2.SetSpeedPercent(speed)

    def Run(self):
        while self.running:
            self.FollowLine()
            time.sleep(0.02)  # 20 ms delay between control updates

    def Start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.Run)
            self.thread.start()

    def Stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.motor1.SetSpeedPercent(0)
        self.motor2.SetSpeedPercent(0)
