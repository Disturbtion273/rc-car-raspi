class ModeManager:
    def __init__(self, manualMode, semiAiMode, fullAiMode, mode="None"):
        self.modes = {
            "None": None,
            "Manual": manualMode,
            "SemiAi": semiAiMode,
            "FullAi": fullAiMode
        }
        self.modeName = mode
        self.mode = self.modes[mode]

    def SetMode(self, mode):
        if mode in self.modes:
            if self.modeName != mode:
                self.mode.Stop() if self.mode is not None else None
                self.modeName = mode
                self.mode = self.modes[mode]
                print(f"Mode is set to: {self.modeName}")
                if self.mode is not None:
                    self.mode.Start()
            else:
                print(f"Mode '{mode}' is already active. No change made.")
        else:
            print(f"Invalid mode: {mode}. Available modes: {list(self.modes.keys())}")

    def HandleMessage(self, message):
        if self.mode is not None:
            self.mode.HandleMessage(message)
        else:
            print("No mode selected to handle the message.")