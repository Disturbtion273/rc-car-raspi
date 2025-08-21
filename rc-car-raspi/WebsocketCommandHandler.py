import json

class WebsocketCommandHandler:
    def __init__(self, motor1, motor2, servoTilt, servoPan, servoSteering):
        self.motorLeft = motor1
        self.motorRight = motor2
        self.servoTilt = servoTilt
        self.servoPan = servoPan
        self.servoSteering = servoSteering

    def handleMessage(self, message):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print("⚠ Invalid JSON received:", message)
            return

        if "speed" in data:
            self.motorLeft.SetSpeedPercent(data["speed"])
            self.motorRight.SetSpeedPercent(data["speed"])

        if "steering" in data:
            self.servoSteering.SetAnglePercent(data["steering"])

        if "tilt" in data and "tiltSpeed" in data:
            self.servoTilt.SetMovement(data["tilt"], data["tiltSpeed"])

        if "pan" in data and "panSpeed" in data:
            self.servoPan.SetMovement(data["pan"],data["panSpeed"])

        # Warn about unknown keys
        knownKeys = {"speed", "steering", "tilt", "pan", "tiltSpeed", "panSpeed"}
        for key in data.keys():
            if key not in knownKeys:
                print(f"⚠ Unknown command key: '{key}'")