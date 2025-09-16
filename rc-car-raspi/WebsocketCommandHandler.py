import json
import ModeManager

class WebsocketCommandHandler:
    def __init__(self, modeManager, aiCommandHandler):
        self.modeManager = modeManager
        self.aiCommandHandler = aiCommandHandler

    def HandleMessage(self, message):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print("⚠ Invalid JSON received:", message)
            return

        # Warn about unknown keys
        knownKeys = {"speed", "steering", "tilt", "pan", "tiltSpeed", "panSpeed", "cameraReset", "drivingMode", "intersectionDirection"}
        for key in data.keys():
            if key == "intersectionDirection" and self.modeManager.currentMode == "automatic":
                self.aiCommandHandler.HandleIntersectionDirection(data["intersectionDirection"])
            elif key in knownKeys:
                self.modeManager.HandleMessage(data)
            else:
                print(f"⚠ Unknown command key: '{key}'")

    
        

        

        