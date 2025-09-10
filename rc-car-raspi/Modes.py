import json

class ManualMode():
    def __init__(self, websocketServer, cameraStream, driving, servoTilt, servoPan):
        self.websocketServer = websocketServer
        self.cameraStream = cameraStream
        self.driving = driving
        self.servoTilt = servoTilt
        self.servoPan = servoPan

    def Start(self):
        print("Manual Mode starts.")
        self.cameraStream.Start()

    def Stop(self):
        print("Manual Mode stopping.")
        # Reset servos or driving
        self.servoTilt.SetAnglePercent(50)
        self.servoPan.SetAnglePercent(50)
        self.driving.SetSpeedPercent(0)
        self.driving.SetSteeringPercent(0)

    def HandleMessage(self, message):
        data = message
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


class SemiAiMode():
    def __init__(self, websocketServer, cameraStream, driving, servoTilt, servoPan, aiCommandHandler):
        self.websocketServer = websocketServer
        self.cameraStream = cameraStream
        self.driving = driving
        self.servoTilt = servoTilt
        self.servoPan = servoPan
        self.aiCommandHandler = aiCommandHandler

    def Start(self):
        print("Semi-AI Mode gestartet.")
        self.cameraStream.Start()
        self.aiCommandHandler.Start()

    def Stop(self):
        self.aiCommandHandler.Stop()

    def HandleMessage(self, message):
        data = message
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


class FullAiMode():
    def __init__(self, lineFollower, aiCommandHandler, servoPan, servoTilt):
        self.lineFollower = lineFollower
        self.aiCommandHandler = aiCommandHandler
        self.servoPan = servoPan
        self.servoTilt = servoTilt

    def Start(self):
        print("Full-AI Mode gestartet.")
        self.lineFollower.Start()
        self.aiCommandHandler.Start()
        self.servoPan.SetAnglePercent(50)
        self.servoTilt.SetAnglePercent(50)

    def Stop(self):
        self.aiCommandHandler.Stop()
        self.lineFollower.Stop()
        print("Full-AI Mode stopping.")

    def HandleMessage(self, message):
        pass
 
 