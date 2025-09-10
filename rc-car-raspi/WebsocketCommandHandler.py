import json
import ModeManager

class WebsocketCommandHandler:
    def __init__(self, modeManager, intersection):
        self.modeManager = modeManager
        self.intersection = intersection

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
                self.intersection.SetIntersectionDirection(data["intersectionDirection"])
                # Also notify AiCommandHandler about the intersection direction
                if hasattr(self.intersection, 'aiCommandHandler'):
                    self.intersection.aiCommandHandler.HandleIntersectionDirection(data["intersectionDirection"])
            elif key in knownKeys:
                self.modeManager.HandleMessage(data)
            else:
                print(f"⚠ Unknown command key: '{key}'")

    
        

        

        