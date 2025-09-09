class ModeManager:
    currentMode = None
    def __init__(self, manualMode, semiAiMode, fullAiMode, mode="none"):
        self.modes = {
            "none": None,
            "manual": manualMode,
            "semiautomatic": semiAiMode,
            "automatic": fullAiMode
        }
        self.modeName = mode
        self.mode = self.modes[mode]
        ModeManager.currentMode = self.mode

    def SetMode(self, mode):
        if mode in self.modes:
            if self.modeName != mode:
                self.mode.Stop() if self.mode is not None else None
                self.modeName = mode
                self.mode = self.modes[mode]
                ModeManager.currentMode = self.modeName
                print(f"Mode is set to: {self.modeName}")
                if self.mode is not None:
                    self.mode.Start()
            else:
                print(f"Mode '{mode}' is already active. No change made.")
        else:
            print(f"Invalid mode: {mode}. Available modes: {list(self.modes.keys())}")

    def HandleMessage(self, message):
        if "drivingMode" in message:
            self.SetMode(message["drivingMode"])
        if self.mode is not None:
            self.mode.HandleMessage(message)
 
 