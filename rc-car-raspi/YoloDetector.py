import os
import time
import threading
import cv2
import numpy as np
from ultralytics import YOLO
from flask import Flask, Response
from CameraManager import CameraManager


class YoloDetector:
    def __init__(self):
        # Konfiguration
        self.modelPath = './yolo_model/my_model_11s_ncnn_model'
        self.resolution = (1080, 800)
        self.minConfidence = 0.5
        self.bboxColors = [
            (164, 120, 87), (68, 148, 228), (93, 97, 209), (178, 182, 133),
            (88, 159, 106), (96, 202, 231), (159, 124, 168), (169, 162, 241),
            (98, 118, 150), (172, 176, 184)
        ]

        # Modell laden
        if not os.path.exists(self.modelPath):
            raise FileNotFoundError(f"Modell nicht gefunden: {self.modelPath}")
        self.model = YOLO(self.modelPath, task='detect')
        self.labels = self.model.names

        # Singleton CameraManager verwenden
        self.cameraManager = CameraManager()

        # Flask App und Streaming
        self.app = Flask(__name__)
        self.frameRateBuffer = []
        self.fpsAvgLen = 50
        self.avgFps = 0
        self.streamingThread = None
        self.SetupRoutes()

    def SetupRoutes(self):
        @self.app.route('/')
        def VideoFeed():
            return Response(self.GenerateFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def StartStreaming(self, host='0.0.0.0', port=8080):
        def RunFlask():
            self.app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

        self.streamingThread = threading.Thread(target=RunFlask, daemon=True)
        self.streamingThread.start()
        print(f"Camera stream running at http://{host}:{port}/")

    def GenerateFrames(self):
        while True:
            frame = self.cameraManager.GetLatestFrame()
            if frame is None:
                time.sleep(0.01)
                continue

            tStart = time.perf_counter()

            # YOLO Inferenz
            results = self.model(frame, verbose=False)
            detections = results[0].boxes
            for det in detections:
                xyxy = det.xyxy.cpu().numpy().squeeze().astype(int)
                xmin, ymin, xmax, ymax = xyxy
                classIdx = int(det.cls.item())
                conf = det.conf.item()
                if conf > self.minConfidence:
                    color = self.bboxColors[classIdx % len(self.bboxColors)]
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                    label = f"{self.labels[classIdx]}: {int(conf * 100)}%"
                    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    labelYmin = max(ymin, labelSize[1] + 10)
                    cv2.rectangle(frame, (xmin, labelYmin - labelSize[1] - 10),
                                  (xmin + labelSize[0], labelYmin + baseLine - 10), color, cv2.FILLED)
                    cv2.putText(frame, label, (xmin, labelYmin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # FPS berechnen
            tStop = time.perf_counter()
            frameFps = 1 / (tStop - tStart)
            self.frameRateBuffer.append(frameFps)
            if len(self.frameRateBuffer) > self.fpsAvgLen:
                self.frameRateBuffer.pop(0)
            self.avgFps = np.mean(self.frameRateBuffer)
            cv2.putText(frame, f"FPS: {self.avgFps:.1f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
            if not ret:
                continue
            frameBytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frameBytes + b'\r\n')

    def DetectSingleImage(self):
        frame = self.cameraManager.GetLatestFrame()
        if frame is None:
            print("Kein Kamerabild verfügbar.")
        results = self.model(frame, verbose=False)
        detections = results[0].boxes

        resultList = []
        for det in detections:
            classIdx = int(det.cls.item())
            conf = det.conf.item()
            if conf > self.minConfidence:
                label = self.labels[classIdx]
                resultList.append((label, conf))

        return resultList

 