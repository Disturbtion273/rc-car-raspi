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

        self.threshold = 0.45  # Confidence threshold for detections
        self.fps = 3 #Dections per second
        self.timeOfDetection = 1 # seconds neeed to confirm detection

        self.currentNumberOfDetections = 0
        self.needNumberOfDetections = self.fps * self.timeOfDetection
        self.lastDetectedLabel = None

        # High confidence parameters  
        self.highConfidenceThreshold = 0.70
        self.needNumberOfHighConfidenceDetections = 2
        self.currentNumberOfHighConfidenceDetections = 0

        self.detectedSign = None
        self.isSignDetected = False
        self.needSizeWidthPercent = 14

        self.signCooldowns = {}  # Stores last handled times for signs
        self.cooldownDuration = 7  # seconds
        
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
            time.sleep(1/self.fps)

    def DetectionConfirmer(self, detectedLabels):
        labelWithMaxProbability, probability, sizePercent = max(detectedLabels, key=lambda x: x[1])
        print("Size" + str(sizePercent))

        # Exception for intersection sign
        if not self.waitingForIntersectionDirection and labelWithMaxProbability == "kreuzung" and probability >= 0.5 and sizePercent >= 14:
            self.HandleDetection(labelWithMaxProbability)
            return

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

    def IsSignNearEnough(self, labelWithMaxProbability, sizePercent):
        now = time.time()

        # Check if the sign is on cooldown
        if labelWithMaxProbability in self.signCooldowns:
            time_since_last_detection = now - self.signCooldowns[labelWithMaxProbability]
            if time_since_last_detection < self.cooldownDuration:
                print(f"{labelWithMaxProbability} is on cooldown ({int(self.cooldownDuration - time_since_last_detection)}s left). Skipping.")
                return

        # Exception for sackgasse sign
        if self.isSignDetected and self.needSizeWidthPercent <= sizePercent or (labelWithMaxProbability == "sackgasse" and sizePercent <= 16) and labelWithMaxProbability == self.detectedSign :
            print("Label detected:" + labelWithMaxProbability)
            self.HandleDetection(self.detectedSign)
            self.isSignDetected = False
            self.detectedSign = None


    def SignDetection(self, label):
        print("Sign Detected")
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
                saveSpeedForReset = self.driving.currentSpeed
                self.driving.SetMaxSpeedPercent(self.driving.currentSpeed/2)

                def resetSpeed():
                    self.driving.SetMaxSpeedPercent(saveSpeedForReset)
                    self.driving.SetSpeedPercent(saveSpeedForReset)

                timer = threading.Timer(3.0, resetSpeed)
                timer.start()
            self.spokenNameOfSign = "Achtung"

        elif label =="stopp":
            if ModeManager.ModeManager.currentMode == "automatic":
                saveSpeedForReset = self.driving.currentSpeed
                self.driving.SetMaxSpeedPercent(0)

                def continueDriving():
                    self.driving.SetMaxSpeedPercent(saveSpeedForReset)
                    self.driving.SetSpeedPercent(saveSpeedForReset)
                
                timer = threading.Timer(2.0, continueDriving)
                timer.start()
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

                timer = threading.Timer(4.0, continueCenterDriving)
                timer.start()
            self.spokenNameOfSign="Abbiegen"

        elif label == "durchfahrt_verboten":
            if ModeManager.ModeManager.currentMode == "automatic":
                self.lineFollower.SetDirection("right")

                def continueCenterDriving():
                    self.lineFollower.SetDirection("center")

                timer = threading.Timer(4.0, continueCenterDriving)
                timer.start()
            self.spokenNameOfSign="Durchfahrt Verboten"

        elif label == "kreuzung":
            if ModeManager.ModeManager.currentMode == "automatic":
                if not self.waitingForIntersectionDirection:
                    self.intersection.StartIntersection()
                    self.waitingForIntersectionDirection = True
                    print("Kreuzung erkannt - waiting for direction")
                else:
                    print("Already waiting for intersection direction")

            self.spokenNameOfSign="Kreuzung"

        if label != "kreuzung":
            self.signCooldowns[label] = time.time()

        self.SendDetectedLabel(label)
        self.Speaker.Speak(self.spokenNameOfSign)

    def HandleIntersectionDirection(self, direction):
        if self.waitingForIntersectionDirection:
            print(f"Received intersection direction: {direction}")
            self.waitingForIntersectionDirection = False            
            self.signCooldowns["kreuzung"] = time.time() 




