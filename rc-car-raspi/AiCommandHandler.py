import threading
import time
import ModeManager
import json

class AiCommandHandler:
    def __init__(self, driving, yoloDetector, websocketServer):
        self.driving = driving
        self.yoloDetector = yoloDetector
        self.websocketServer = websocketServer

        self._running = False
        self._detect_thread = None

        self.threshold = 0.6  # Confidence threshold for detections
        self.fps = 3 #Dections per second
        self.timeOfDetection = 1 # seconds neeed to confirm detection

        self.currentNumberOfDetections = 0
        self.needNumberOfDetections = self.fps * self.timeOfDetection
        self.lastDetectedLabel = None

        # High confidence parameters  
        self.highConfidenceThreshold = 0.9
        self.needNumberOfHighConfidenceDetections = 2
        self.currentNumberOfHighConfidenceDetections = 0

        self.detectedSign = None
        self.isSignDetected = False
        self.needSizeWidthPercent = 18


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
        labelWithMaxProbability, probability, sizePercent = max(detectedLabels, key=lambda x: x[1])
        print("Size" + str(sizePercent))

        self.IsSignNearEnough(labelWithMaxProbability, sizePercent)

        if labelWithMaxProbability == self.lastDetectedLabel:
            if probability >= self.threshold:
                self.currentNumberOfDetections += 1
            else:
                self.currentNumberOfDetections = 0

            if probability >= self.highConfidenceThreshold:
                self.currentNumberOfHighConfidenceDetections += 1
            else:
                self.currentNumberOfHighConfidenceDetections = 0
        else:
            self.lastDetectedLabel = labelWithMaxProbability
            self.currentNumberOfDetections =  0
            self.currentNumberOfHighConfidenceDetections = 0

        if self.currentNumberOfDetections >= self.needNumberOfDetections or self.currentNumberOfHighConfidenceDetections >= 2:
            self.SignDetection(labelWithMaxProbability)
            self.IsSignNearEnough(labelWithMaxProbability, sizePercent)
            self.currentNumberOfDetections = 0
            self.currentNumberOfHighConfidenceDetections = 0
            self.lastDetectedLabel = None

    def SendDetectedLabel(self, label):
        if self.websocketServer:
            message = json.dumps({"label": label})
            self.websocketServer.Send(message)

    def IsSignNearEnough(self, labelWithMaxProbability ,sizePercent):
        if self.isSignDetected and self.needSizeWidthPercent <= sizePercent and labelWithMaxProbability == self.detectedSign:
            self.HandleDetection(self.detectedSign)
            self.signDetected = False
            self.detectedSign = None

    def SignDetection(self, label):
        print("Sign Detected")
        self.isSignDetected = True
        self.detectedSign = label

    def HandleDetection(self, label):
        if label == "unbegrenzt":
            if ModeManager.ModeManager.currentMode == "automatic":
                self.driving.SetMaxSpeedPercent(50)
            else:
                self.SetMaxSpeedPercent(100)
            print("Unbegrenzt erkannt")

        elif label == "fuenfzig":
            if ModeManager.ModeManager.currentMode == "automatic":
                self.driving.SetMaxSpeedPercent(25)
            else:
                self.driving.SetMaxSpeedPercent(50)
            print("50 erkannt")

        elif label == "dreissig":
            if ModeManager.ModeManager.currentMode == "automatic":
                self.driving.SetMaxSpeedPercent(15)
            else:
                self.driving.SetMaxSpeedPercent(30)
            print("30 erkannt")

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

        elif label == "sackgasse":
            if ModeManager.ModeManager.currentMode == "automatic":
                self.driving.SetSpeedPercent(0)
                print("Sackgasse erkannt")

        self.SendDetectedLabel(label)


   

    