import threading
import time
import ModeManager
import json
from Speaker import Speaker as Speaker

class AiCommandHandler:
    Speaker = Speaker

    def __init__(self, driving, lineFollower, yoloDetector, websocketServer, intersection):
        self.driving = driving
        self.lineFollower = lineFollower
        self.yoloDetector = yoloDetector
        self.websocketServer = websocketServer
        self.intersection = intersection

        self._running = False
        self._detect_thread = None

        self.threshold = 0.45  
        self.fps = 2  

        self.currentNumberOfDetections = 0
        self.lastDetectedLabel = None

        self.detectedSign = None
        self.isSignDetected = False
        self.needSizeWidthPercent = 13

        self.signCooldowns = {} 
        self.cooldownDuration = 7  

        self.waitingForIntersectionDirection = False

        self.spokenNameOfSign = ""

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
            time.sleep(1 / self.fps)

    def DetectionConfirmer(self, detectedLabels):
        labelWithMaxProbability, probability, sizePercent = max(detectedLabels, key=lambda x: x[1])

        self.IsSignNearEnough(labelWithMaxProbability, sizePercent)

        if probability < self.threshold:
            print(f"Label {labelWithMaxProbability} erkannt, aber Wahrscheinlichkeit zu niedrig ({probability:.2f})")
            return

        if labelWithMaxProbability == self.lastDetectedLabel:
            self.currentNumberOfDetections += 1
            print(f"Label {labelWithMaxProbability} erneut erkannt ({self.currentNumberOfDetections}/2)")

            if self.currentNumberOfDetections >= 2:
                self.SignDetection(labelWithMaxProbability)
                self.IsSignNearEnough(labelWithMaxProbability, sizePercent)
        else:
            print(f"Anderes Label erkannt ({labelWithMaxProbability}), Zähler wird zurückgesetzt.")
            self.lastDetectedLabel = labelWithMaxProbability
            self.currentNumberOfDetections = 1

    def SendDetectedLabel(self, label):
        if self.websocketServer:
            message = json.dumps({"label": label})
            self.websocketServer.Send(message)

    def IsSignNearEnough(self, labelWithMaxProbability, sizePercent):
        now = time.time()

        if labelWithMaxProbability in self.signCooldowns:
            time_since_last_detection = now - self.signCooldowns[labelWithMaxProbability]
            if time_since_last_detection < self.cooldownDuration:
                print(f"{labelWithMaxProbability} ist im Cooldown ({int(self.cooldownDuration - time_since_last_detection)}s übrig).")
                return

        if self.isSignDetected and self.needSizeWidthPercent <= sizePercent or (labelWithMaxProbability == "sackgasse" and sizePercent <= 16) and labelWithMaxProbability == self.detectedSign:
            print("Label erkannt: " + labelWithMaxProbability)
            self.HandleDetection(self.detectedSign)
            self.isSignDetected = False
            self.detectedSign = None

    def SignDetection(self, label):
        self.isSignDetected = True
        self.detectedSign = label

    def HandleDetection(self, label):
        if label == "unbegrenzt":
            if ModeManager.ModeManager.currentMode == "automatic":
                self.driving.SetMaxSpeedPercent(50)
            self.spokenNameOfSign = "Unbegrenzt"

        elif label == "fuenfzig":
            if ModeManager.ModeManager.currentMode == "automatic":
                self.driving.SetMaxSpeedPercent(30)
            self.spokenNameOfSign = "Fünfzig"

        elif label == "dreissig":
            if ModeManager.ModeManager.currentMode == "automatic":
                self.driving.SetMaxSpeedPercent(20)
            self.spokenNameOfSign = "Dreissig"

        elif label == "achtung":
            if ModeManager.ModeManager.currentMode == "automatic":
                saveSpeed = self.driving.currentSpeed
                self.driving.SetMaxSpeedPercent(saveSpeed / 2)

                def resetSpeed():
                    self.driving.SetMaxSpeedPercent(saveSpeed)
                    self.driving.SetSpeedPercent(saveSpeed)

                threading.Timer(3.0, resetSpeed).start()
            self.spokenNameOfSign = "Achtung"

        elif label == "stopp":
            if ModeManager.ModeManager.currentMode == "automatic":
                saveSpeed = self.driving.currentSpeed
                self.driving.SetMaxSpeedPercent(0)

                def continueDriving():
                    self.driving.SetMaxSpeedPercent(saveSpeed)
                    self.driving.SetSpeedPercent(saveSpeed)

                threading.Timer(2.0, continueDriving).start()
            self.spokenNameOfSign = "Stopp"

        elif label == "sackgasse":
            if ModeManager.ModeManager.currentMode == "automatic":
                self.driving.SetMaxSpeedPercent(0)
            self.spokenNameOfSign = "Sackgasse"

        elif label == "abbiegen":
            if ModeManager.ModeManager.currentMode == "automatic":
                self.lineFollower.SetDirection("right")

                def continueCenterDriving():
                    self.lineFollower.SetDirection("center")

                threading.Timer(4.0, continueCenterDriving).start()
            self.spokenNameOfSign = "Abbiegen"

        elif label == "durchfahrt_verboten":
            if ModeManager.ModeManager.currentMode == "automatic":
                self.lineFollower.SetDirection("right")

                def continueCenterDriving():
                    self.lineFollower.SetDirection("center")

                threading.Timer(4.0, continueCenterDriving).start()
            self.spokenNameOfSign = "Durchfahrt Verboten"

        elif label == "kreuzung":
            if ModeManager.ModeManager.currentMode == "automatic":
                if not self.waitingForIntersectionDirection:
                    self.intersection.StartIntersection()
                    self.waitingForIntersectionDirection = True
                    print("Kreuzung erkannt – warte auf Richtung.")
                else:
                    print("Bereits in Kreuzungsmodus.")
            self.spokenNameOfSign = "Kreuzung"

        if label == "kreuzung" and not self.waitingForIntersectionDirection:
            self.SendDetectedLabel(label)
            self.Speaker.Speak(self.spokenNameOfSign)

        self.currentNumberOfDetections = 0
        self.lastDetectedLabel = None
        
    def HandleIntersectionDirection(self, direction):
        if self.waitingForIntersectionDirection:
            print(f"Kreuzungsrichtung erhalten: {direction}")
            self.intersection.SetIntersectionDirection(direction)
            self.waitingForIntersectionDirection = False
            self.signCooldowns["kreuzung"] = time.time()
