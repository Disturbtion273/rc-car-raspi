import os
import sys
import argparse
import time
import threading
import cv2
import numpy as np
from ultralytics import YOLO
from flask import Flask, Response
from picamera2 import Picamera2

# ------------------------------
# Argument Parser
# ------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--model', required=True, help='Path to YOLO model file')
parser.add_argument('--thresh', default=0.5, type=float, help='Minimum confidence threshold')
parser.add_argument('--resolution', default='640x480', help='Resolution WxH')
args = parser.parse_args()

# ------------------------------
# Load YOLO Model
# ------------------------------
if not os.path.exists(args.model):
    print("ERROR: Model path not found.")
    sys.exit(0)

model = YOLO(args.model, task='detect')
labels = model.names

resW, resH = map(int, args.resolution.split('x'))

# ------------------------------
# Initialize Camera
# ------------------------------
camera = Picamera2()
camera_config = camera.create_video_configuration(
    main={"size": (resW, resH), "format": "RGB888"},
    controls={"FrameRate": 20}
)
camera.configure(camera_config)
camera.start()

# ------------------------------
# Bounding Box Colors
# ------------------------------
bbox_colors = [
    (164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106),
    (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)
]

# ------------------------------
# Flask Camera Streaming Class
# ------------------------------
class CameraStream(threading.Thread):
    def __init__(self, camera, host='0.0.0.0', port=8080):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.camera = camera
        self.avg_fps = 0
        self.frame_rate_buffer = []
        self.fps_avg_len = 50
        self.min_thresh = args.thresh
        self.SetupRoutes()

    def run(self):
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False, threaded=True)

    def SetupRoutes(self):
        @self.app.route('/')
        def video_feed():
            return Response(self.GenerateFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def GenerateFrames(self):
        while True:
            t_start = time.perf_counter()
            frame = self.camera.capture_array()

            # YOLO Inference
            results = model(frame, verbose=False)
            detections = results[0].boxes
            for det in detections:
                xyxy = det.xyxy.cpu().numpy().squeeze().astype(int)
                xmin, ymin, xmax, ymax = xyxy
                classidx = int(det.cls.item())
                conf = det.conf.item()
                if conf > self.min_thresh:
                    color = bbox_colors[classidx % 10]
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                    label = f"{labels[classidx]}: {int(conf*100)}%"
                    label_size, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    label_ymin = max(ymin, label_size[1] + 10)
                    cv2.rectangle(frame, (xmin, label_ymin-label_size[1]-10), (xmin+label_size[0], label_ymin+baseLine-10), color, cv2.FILLED)
                    cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)

            # FPS Berechnung
            t_stop = time.perf_counter()
            frame_fps = 1 / (t_stop - t_start)
            self.frame_rate_buffer.append(frame_fps)
            if len(self.frame_rate_buffer) > self.fps_avg_len:
                self.frame_rate_buffer.pop(0)
            self.avg_fps = np.mean(self.frame_rate_buffer)
            cv2.putText(frame, f"FPS: {self.avg_fps:.1f}", (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# ------------------------------
# Start Streaming
# ------------------------------
stream = CameraStream(camera)
stream.start()
print("Camera stream running at http://<raspi-ip>:8080/")

# ------------------------------
# Keep main thread alive
# ------------------------------
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping...")
    camera.stop()
