import json

class WebsocketCommandHandler:
    def __init__(self, driving, servoTilt, servoPan):
        self.driving = driving
        self.servoTilt = servoTilt
        self.servoPan = servoPan

    def handleMessage(self, message):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print("⚠ Invalid JSON received:", message)
            return

        if "speed" in data:
            self.driving.SetSpeedPercent(data["speed"])

        if "steering" in data:
            self.driving.SetSteeringPercent(data["steering"])

        if "tilt" in data and "tiltSpeed" in data:
            self.servoTilt.SetMovement(data["tilt"], data["tiltSpeed"])

        if "pan" in data and "panSpeed" in data:
            self.servoPan.SetMovement(data["pan"],data["panSpeed"])

        if "cameraReset" in data:
            if data["cameraReset"]:
                self.servoTilt.SetAnglePercent(50)
                self.servoPan.SetAnglePercent(50)

        # Warn about unknown keys
        knownKeys = {"speed", "steering", "tilt", "pan", "tiltSpeed", "panSpeed", "cameraReset"}
        for key in data.keys():
            if key not in knownKeys:
                print(f"⚠ Unknown command key: '{key}'")