import json

class WebsocketCommandHandler:
    def __init__(self, modeManager):
        self.modeManager = modeManager

    def handleMessage(self, message):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print("⚠ Invalid JSON received:", message)
            return

        # Warn about unknown keys
        knownKeys = {"speed", "steering", "tilt", "pan", "tiltSpeed", "panSpeed", "cameraReset"}
        for key in data.keys():
            if key not in knownKeys:
                print(f"⚠ Unknown command key: '{key}'")

        self.modeManager.HandleMessage(message)

        

        