import threading
import time

class AiCommandHandler:
    def __init__(self, driving, yoloDetector):
        self.driving = driving
        self.yoloDetector = yoloDetector

        self._running = False
        self._detect_thread = None

        self.threshold = 0.7  # Confidence threshold for detections
        self.fps = 3 #Dections per second
        self.timeOfDetection = 2 # seconds neeed to confirm detection

        self.currentNumberOfDetections = 0
        self.needNumberOfDetections = self.fps * self.timeOfDetection
        self.lastDetectedLabel = None

    def Start(self):
        if self._running:
            print("YOLO-Thread läuft bereits.")
            return

        self._running = True
        self._detect_thread = threading.Thread(target=self.DetectionLoop, daemon=True)
        self._detect_thread.start()
        print("YOLO-Erkennungs-Thread gestartet.")

    def Stop(self):
        self._running = False
        if self._detect_thread is not None:
            self._detect_thread.join(timeout=1)
            print("YOLO-Erkennungs-Thread gestoppt.")

    def DetectionLoop(self):
        while self._running:
            detected = self.yoloDetector.DetectSingleImage()
            print(detected)
            if detected:
                self.DetectionConfirmer(detected)
            else:
                self.currentNumberOfDetections = 0
                print("Kein Label erkannt.")
            time.sleep(1/self.fps)

    def DetectionConfirmer(self, detectedLabels):
        labelWithMaxProbability = max(detectedLabels, key=lambda x: x[1])[0]
        probabilityOfMaxLabel = max(detectedLabels, key=lambda x: x[1])[1]
        if labelWithMaxProbability == self.lastDetectedLabel and probabilityOfMaxLabel >= self.threshold:
            self.currentNumberOfDetections += 1
        else:
            self.currentNumberOfDetections = 1
            self.lastDetectedLabel = labelWithMaxProbability

        if self.currentNumberOfDetections >= self.needNumberOfDetections:
            self.HandleDetection(labelWithMaxProbability)
            self.currentNumberOfDetections = 0
            self.lastDetectedLabel = None

    def HandleDetection(self, label):
        if label == "unbegrenzt":
            self.driving.SetMaxSpeedPercent(100)
            print("Unbegrenzt erkannt")

        elif label == "fuenfzig":
            self.driving.SetMaxSpeedPercent(50)
            print("50 erkannt")

        elif label == "achtung":
            print("Achtung erkannt")
            saveSpeedForReset = self.driving.currentSpeed
            self.driving.SetMaxSpeedPercent(self.driving.currentSpeed/2)
            def resetSpeed():
                self.driving.SetMaxSpeedPercent(saveSpeedForReset)
                self.driving.SetSpeedPercent(saveSpeedForReset)
            timer = threading.Timer(3.0, resetSpeed)
            timer.start()

        elif label =="stopp":
            print("Stop erkannt")
            saveSpeedForReset = self.driving.currentSpeed
            self.driving.SetMaxSpeedPercent(0)

            def continueDriving():
                self.driving.SetMaxSpeedPercent(saveSpeedForReset)
                self.driving.SetSpeedPercent(saveSpeedForReset)

            timer = threading.Timer(2.0, continueDriving)
            timer.start()
    

    
