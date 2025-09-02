import threading
import time
import cv2
from CameraManager import CameraManager
from flask import Flask, Response


class CameraStream(threading.Thread):
    def __init__(self, host='0.0.0.0', port=8080):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.cameraManager = CameraManager()
        self.SetupRoutes()

    def run(self):
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False, threaded=True)

    def SetupRoutes(self):
        @self.app.route('/')
        def videoFeed():
            return Response(self.GenerateFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def GenerateFrames(self):
        while True:
            frame = self.cameraManager.GetLatestFrame()
            if frame is None:
                time.sleep(0.01)
                continue

            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
            if not ret:
                continue

            frameBytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frameBytes + b'\r\n')
