import json

class WebsocketCommandHandler:
    def __init__(self, motor1, motor2, servoTilt, servoPan, servoSteering):
        self.motorLeft = motor1
        self.motorRight = motor2
        self.servoTilt = servoTilt
        self.servoPan = servoPan
        self.servoSteering = servoSteering

    async def handleMessage(self, message):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print("⚠ Invalid JSON received:", message)
            return

        command = data.get("command")
        value = data.get("value")

        if command is None or value is None:
            print("⚠ Error in Message:", data)
            return

        match command:
            case "drive":
                self.motorLeft.SetSpeedPercent(value)
                self.motorRight.SetSpeedPercent(value)
            case "steering":
                self.servoSteering.SetAnglePercent(value)
            case "tilt":
                self.servoTilt.SetAnglePercent(value)
            case "pan":
                self.servoPan.SetAnglePercent(value)
            case _:
                print(f"⚠ Unknown Command: {command}")