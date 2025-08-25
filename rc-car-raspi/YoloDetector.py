import os
import time
import threading
import cv2
import numpy as np
from ultralytics import YOLO
from flask import Flask, Response
from picamera2 import Picamera2


class YoloDetector:
    def __init__(self):
        # Konfiguration
        self.model_path = 'my_model_11s_ncnn_model'
        self.resolution = (1280, 720)
        self.min_confidence = 0.5
        self.bbox_colors = [
            (164, 120, 87), (68, 148, 228), (93, 97, 209), (178, 182, 133),
            (88, 159, 106), (96, 202, 231), (159, 124, 168), (169, 162, 241),
            (98, 118, 150), (172, 176, 184)
        ]

        # Modell laden
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modell nicht gefunden: {self.model_path}")
        self.model = YOLO(self.model_path, task='detect')
        self.labels = self.model.names

        # Kamera-Objekt, aber noch nicht initialisiert/startet
        self.camera = None

        # Flask
        self.app = Flask(__name__)
        self.frame_rate_buffer = []
        self.fps_avg_len = 50
        self.avg_fps = 0
        self.streaming_thread = None
        self._setup_routes()

    def start_camera(self):
        if self.camera is None:
            self.camera = Picamera2()
            camera_config = self.camera.create_video_configuration(
                main={"size": self.resolution, "format": "RGB888"},
                controls={"FrameRate": 20}
            )
            self.camera.configure(camera_config)
            self.camera.start()
            print("Kamera gestartet.")
        else:
            print("Kamera ist bereits gestartet.")

    def _setup_routes(self):
        @self.app.route('/')
        def video_feed():
            return Response(self._generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def start_streaming(self, host='0.0.0.0', port=8080):
        def run_flask():
            self.app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

        self.streaming_thread = threading.Thread(target=run_flask, daemon=True)
        self.streaming_thread.start()
        print(f"Camera stream running at http://{host}:{port}/")

    def _generate_frames(self):
        while True:
            if self.camera is None:
                time.sleep(0.1)
                continue

            t_start = time.perf_counter()
            frame = self.camera.capture_array()

            # YOLO Inferenz
            results = self.model(frame, verbose=False)
            detections = results[0].boxes
            for det in detections:
                xyxy = det.xyxy.cpu().numpy().squeeze().astype(int)
                xmin, ymin, xmax, ymax = xyxy
                classidx = int(det.cls.item())
                conf = det.conf.item()
                if conf > self.min_confidence:
                    color = self.bbox_colors[classidx % len(self.bbox_colors)]
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                    label = f"{self.labels[classidx]}: {int(conf * 100)}%"
                    label_size, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    label_ymin = max(ymin, label_size[1] + 10)
                    cv2.rectangle(frame, (xmin, label_ymin - label_size[1] - 10),
                                  (xmin + label_size[0], label_ymin + baseLine - 10), color, cv2.FILLED)
                    cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # FPS berechnen
            t_stop = time.perf_counter()
            frame_fps = 1 / (t_stop - t_start)
            self.frame_rate_buffer.append(frame_fps)
            if len(self.frame_rate_buffer) > self.fps_avg_len:
                self.frame_rate_buffer.pop(0)
            self.avg_fps = np.mean(self.frame_rate_buffer)
            cv2.putText(frame, f"FPS: {self.avg_fps:.1f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # JPEG kodieren
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    def detect_single_image(self):
        if self.camera is None:
            raise RuntimeError("Kamera ist nicht gestartet. Bitte zuerst start_camera() aufrufen.")
        frame = self.camera.capture_array()
        results = self.model(frame, verbose=False)
        detections = results[0].boxes

        result_list = []
        for det in detections:
            classidx = int(det.cls.item())
            conf = det.conf.item()
            if conf > self.min_confidence:
                label = self.labels[classidx]
                result_list.append(f"{label} ({int(conf * 100)}%)")

        return result_list

    def stop(self):
        if self.camera is not None:
            self.camera.stop()
            self.camera = None
            print("Kamera gestoppt.")
        else:
            print("Kamera war nicht gestartet.")

    
