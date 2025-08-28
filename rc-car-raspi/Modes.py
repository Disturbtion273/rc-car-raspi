import json

class BaseMode:
    def __init__(self):
        pass

    def Start(self):
        """Method to be overridden by subclasses to start the mode."""
        raise NotImplementedError("Start method must be implemented by the subclass.")

    def Stop(self):
        """Method to be overridden by subclasses to stop the mode."""
        raise NotImplementedError("Stop method must be implemented by the subclass.")

    def jsonToData(self, message):
        """Converts a JSON string to a Python dictionary. Returns None if invalid."""
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            print("⚠ Invalid JSON received:", message)
            return None


class ManualMode(BaseMode):
    def __init__(self, websocketServer, cameraStream, driving, servoTilt, servoPan):
        self.websocketServer = websocketServer
        self.cameraStream = cameraStream
        self.driving = driving
        self.servoTilt = servoTilt
        self.servoPan = servoPan

    def Start(self):
        print("Manual Mode starts.")
        self.websocketServer.Start("0.0.0.0", 9999)
        self.cameraStream.start()

    def Stop(self):
        print("Manual Mode stopping.")
        self.websocketServer.Stop()
        self.cameraStream.stop()
        # Optionally reset servos or driving
        self.servoTilt.SetAnglePercent(50)
        self.servoPan.SetAnglePercent(50)
        self.driving.SetSpeedPercent(0)
        self.driving.SetSteeringPercent(0)

    def HandleMessage(self, message):
        data = self.jsonToData(message)
        if not data:
            return

        if "speed" in data:
            self.driving.SetSpeedPercent(data["speed"])

        if "steering" in data:
            self.driving.SetSteeringPercent(data["steering"])

        if "tilt" in data and "tiltSpeed" in data:
            self.servoTilt.SetMovement(data["tilt"], data["tiltSpeed"])

        if "pan" in data and "panSpeed" in data:
            self.servoPan.SetMovement(data["pan"], data["panSpeed"])

        if "cameraReset" in data and data["cameraReset"]:
            self.servoTilt.SetAnglePercent(50)
            self.servoPan.SetAnglePercent(50)


class SemiAiMode(BaseMode):
    def Start(self):
        print("Semi-AI Mode gestartet.")

    def Stop(self):
        print("Semi-AI Mode stopping.")


class FullAiMode(BaseMode):
    def Start(self):
        print("Full-AI Mode gestartet.")

    def Stop(self):
        print("Full-AI Mode stopping.")
