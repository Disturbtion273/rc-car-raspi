class Driving:
    def __init__(self, motor1, motor2, steering):
        self.motor1 = motor1
        self.motor2 = motor2
        self.steering = steering
        self.currentSpeed = 0
        self.maxSpeed = 100
        self.currentSteering = 0

    def SetSpeedPercent(self, speed):
        speed = min(max(speed, -self.maxSpeed), self.maxSpeed)
        self.motor1.SetSpeedPercent(speed)
        self.motor2.SetSpeedPercent(speed)
        self.currentSpeed = speed

    def SetSteeringPercent(self, angle):    
        angle = min(max(angle, 0), 100)
        self.steering.SetAnglePercent(angle)
        self.currentSteering = angle

    def SetMaxSpeedPercent(self, speed):
        self.maxSpeed = min(max(speed, 0), 100)
        print(f"MaxSpeed set to {self.maxSpeed}")
        # Check if car drives backwards and limit speed
        if abs(self.currentSpeed) > self.maxSpeed:
            self.SetSpeedPercent(
                self.maxSpeed if self.currentSpeed > 0 else -self.maxSpeed
            )
