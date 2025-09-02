import json

class WebsocketCommandHandler:
    def __init__(self, modeManager):
        self.modeManager = modeManager

    def HandleMessage(self, message):
        try:
            data = json.loads(message)
            print(data)
        except json.JSONDecodeError:
            print("⚠ Invalid JSON received:", message)
            return

        # Warn about unknown keys
        knownKeys = {"speed", "steering", "tilt", "pan", "tiltSpeed", "panSpeed", "cameraReset", "drivingMode"}
        for key in data.keys():
            if key in knownKeys:
                self.modeManager.HandleMessage(data)
            else:
                print(f"⚠ Unknown command key: '{key}'")

    
        

        

        