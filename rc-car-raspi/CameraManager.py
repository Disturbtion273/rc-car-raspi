import threading
import time
import cv2
from picamera2 import Picamera2

class CameraManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, resolution=(900, 700), framerate=20):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CameraManager, cls).__new__(cls)
                cls._instance.InitCamera(resolution, framerate)
                cls._instance.StartFrameUpdater()
            return cls._instance

    def InitCamera(self, resolution, framerate):
        self.camera = Picamera2()
        config = self.camera.create_video_configuration(
            main={"size": resolution, "format": "RGB888"},
            controls={"FrameRate": framerate}
        )
        self.camera.configure(config)
        self.camera.start()
        self.latestFrame = None
        self.running = True
        print("Kamera initialisiert")

    def StartFrameUpdater(self):
        def update():
            while self.running:
                try:
                    frame = self.camera.capture_array()
                    self.latestFrame = frame
                    time.sleep(1/20)
                except Exception as e:
                    print(f"[CameraManager] Fehler beim Aufnehmen des Frames: {e}")
                    time.sleep(0.5)

        self.updateThread = threading.Thread(target=update, daemon=True)
        self.updateThread.start()

    def GetLatestFrame(self):
        return self.latestFrame.copy() if self.latestFrame is not None else None

    def Stop(self):
        self.running = False
        self.updateThread.join()
        self.camera.stop()
        self.camera.close()
        CameraManager._instance = None
        print("Camera stopped")
 