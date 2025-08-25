import threading
import time

class AiCommandHandler:
    def __init__(self, motorLeft, motorRight, lineFollwer, yoloDetector):
        self.motorLeft = motorLeft
        self.motorRight = motorRight
        self.lineFollwer = lineFollwer
        self.yoloDetector = yoloDetector

        self._running = False
        self._detect_thread = None

    def ChangeSpeed(self, speed):
        self.lineFollwer.SetMaxSpeed(speed)
        self.motorLeft.SetSpeedPercent(speed)
        self.motorRight.SetSpeedPercent(speed)

    def Start(self):
        if self._running:
            print("YOLO-Thread läuft bereits.")
            return

        self._running = True
        self._detect_thread = threading.Thread(target=self._detect_loop, daemon=True)
        self._detect_thread.start()
        print("YOLO-Erkennungs-Thread gestartet.")

    def Stop(self):
        self._running = False
        if self._detect_thread is not None:
            self._detect_thread.join(timeout=1)
            print("YOLO-Erkennungs-Thread gestoppt.")

    def _detect_loop(self):
        while self._running:
            detected = self.yoloDetector.detect_single_image()
            if detected:
                print("Erkannt:", ", ".join(detected))
            else:
                print("Keine Schilder erkannt.")
            time.sleep(0.2)  # 200 ms
