import threading
import cv2
from flask import Flask, Response
from picamera2 import Picamera2


class CameraStream(threading.Thread):
    def __init__(self, host='0.0.0.0', port=8080):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.camera = Picamera2()
        self.SetupCamera()
        self.SetupRoutes()

    def SetupCamera(self):
        config = self.camera.create_video_configuration(
            main={"size": (640, 480), "format": "RGB888"},  
            controls={"FrameRate": 20}
        )
        self.camera.configure(config)
        self.camera.start()

    def SetupRoutes(self):
        @self.app.route('/')
        def videoFeed():
            return Response(self.GenerateFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def GenerateFrames(self):
        while True:
            # Capture a frame from the camera
            frame = self.camera.capture_array()

            # Encode frame as JPEG with quality 65
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
            if not ret:
                continue

            frameBytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frameBytes + b'\r\n')

    def run(self):
        # Start the Flask web server
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False, threaded=True)

    def stop(self):
        self.camera.stop()
        self.camera.close()
