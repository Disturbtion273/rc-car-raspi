#!/usr/bin/env python3

import time
import sys
import socket
import traceback
import sys
import threading
from I2C import I2C
from PWM import PWM
from Motor import Motor
from Data import Data
from Servo import Servo
from GrayscaleSensor import GrayscaleSensor
from UltrasonicSensor import UltrasonicSensor
from Websocket import WebsocketServer
from WebsocketCommandHandler import WebsocketCommandHandler
from CameraStream import CameraStream
from LineFollower import LineFollower
from YoloDetector import YoloDetector
from AiCommandHandler import AiCommandHandler
from Driving import Driving
from ModeManager import ModeManager
from Modes import ManualMode, SemiAiMode, FullAiMode
from CameraManager import CameraManager
from Intersection import Intersection
from Battery import Battery
from Speaker import Speaker

class Main:
    def Initialize(self):
        # Hardware base
        self.i2c = I2C()
        self.pwm = PWM(self.i2c)

        # Motors
        self.motorLeft = Motor(self.pwm, motorNumber=1)
        self.motorRight = Motor(self.pwm, motorNumber=2)

        # Servos
        self.servoPan = Servo(self.pwm, 0)
        self.servoTilt = Servo(self.pwm, 1)
        self.servoSteering = Servo(self.pwm, 2)

        # Sensors
        self.grayscaleSensor = GrayscaleSensor(self.i2c)
        self.ultrasonicSensor = UltrasonicSensor()
        
        # AI / Computer Vision
        self.yoloDetector = YoloDetector()

        # Camera
        self.cameraStream = CameraStream()

        # Center servos
        self.servoSteering.SetAnglePercent(50)  
        self.servoTilt.SetAnglePercent(50)      
        self.servoPan.SetAnglePercent(50)   

        # WebSocket server (placeholder for handler)
        self.websocketServer = WebsocketServer(None)
        self.websocketServer.Start(host='0.0.0.0', port=9999)

        # Driving logic
        self.driving = Driving(self.motorLeft, self.motorRight, self.servoSteering)
        self.lineFollower = LineFollower(driving=self.driving, grayscaleSensor=self.grayscaleSensor)

        self.intersection = Intersection(self.driving, self.lineFollower, self.websocketServer)

        # AI Command Handler (needs to be created before fullAiMode)
        self.aiCommandHandler = AiCommandHandler(self.driving, self.lineFollower, self.yoloDetector, self.websocketServer, self.intersection)

        # Modes
        self.manualMode = ManualMode(self.websocketServer, self.cameraStream, self.driving, self.servoTilt, self.servoPan)
        self.semiAiMode = SemiAiMode(self.websocketServer, self.cameraStream, self.driving, self.servoTilt, self.servoPan, self.aiCommandHandler)
        self.fullAiMode = FullAiMode(self.driving, self.lineFollower, self.aiCommandHandler, self.servoPan, self.servoTilt)
        self.modeManager = ModeManager(self.manualMode, self.semiAiMode, self.fullAiMode, mode="none")

        # WebSocket handler
        self.websocketCommandHandler = WebsocketCommandHandler(self.modeManager, self.intersection)
        self.websocketServer.SetCommandHandler(self.websocketCommandHandler)

        # Camera Manager Singleton
        self.cameraManager = CameraManager()

        # Battery
        self.battery = Battery(self.i2c, self.websocketServer)

        # Speaker
        Speaker.initialize()

    def GetIp(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("192.168.0.1", 1))

            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            return f"Fehler: {e}"

    def Test(self):
        self.Initialize()

        try:
            self.motorLeft.SetSpeedPercent(0)
            self.motorRight.SetSpeedPercent(0)
            time.sleep(1)
            print("----Start Test:----")
            print("Ultrasonic-Sensor-Test beginnt...")
            for i in range(5):
                distance = self.ultrasonicSensor.GetDistance()
                print(f"Entfernung: {distance:.2f} cm")
                time.sleep(0.5)

            print("Grayscale-Sensor-Test beginnt...")
            for i in range(5):
                sensorValue = self.grayscaleSensor.ReadGrayscalePercent(1)
                print(f"Sensor 1 Wert: {sensorValue}")
                sensorValue = self.grayscaleSensor.ReadGrayscalePercent(2)
                print(f"Sensor 2 Wert: {sensorValue}")
                sensorValue = self.grayscaleSensor.ReadGrayscalePercent(3)
                print(f"Sensor 3 Wert: {sensorValue}")
                averageValue = self.grayscaleSensor.ReadAverageGrayscalePercent()
                print(f"Durchschnittswert: {averageValue}")
                time.sleep(0.5)

            print("Servo-Test beginnt...")
            print("Tilt")
            self.servoTilt.SetAnglePercent(0)
            time.sleep(1)
            self.servoTilt.SetAnglePercent(100)
            time.sleep(1)
            self.servoTilt.SetAnglePercent(50)
            time.sleep(1)
            print("Pan")
            self.servoPan.SetAnglePercent(0)
            time.sleep(1)
            self.servoPan.SetAnglePercent(100)
            time.sleep(1)
            self.servoPan.SetAnglePercent(50)
            time.sleep(1)
            print("Steering")
            self.servoSteering.SetAnglePercent(0)
            time.sleep(1)
            self.servoSteering.SetAnglePercent(100)
            time.sleep(1)
            self.servoSteering.SetAnglePercent(50)

            print("Motor-Test beginnt...")
            time.sleep(2)
            print("Vorwärts")
            self.motorLeft.SetSpeedPercent(20)
            self.motorRight.SetSpeedPercent(20)
            time.sleep(1)
            print("Rückwärts")
            self.motorLeft.SetSpeedPercent(-20)
            self.motorRight.SetSpeedPercent(-20)
            time.sleep(1)
            print("Alle Tests beendet.")

        except KeyboardInterrupt:
            print("Beendet durch Benutzer")
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
        finally:
            self.motorLeft.SetSpeedPercent(0)
            self.motorRight.SetSpeedPercent(0)
            self.motorLeft.Cleanup()  
            self.motorRight.Cleanup()
            self.cameraStream.stop()
            self.i2c.Close()
            sys.stdout.flush()
            sys.stderr.flush()

    def Line(self):
        try:
            self.Initialize()
            print("Line Follower startet...")
            self.lineFollower.Start()  
            while True:
                time.sleep(1) 

        except KeyboardInterrupt:
            print("Beendet durch Benutzer")
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
            traceback.print_exc() # Get more details about the error
        finally:
            self.motorLeft.SetSpeedPercent(0)
            self.motorRight.SetSpeedPercent(0)
            self.i2c.Close()
            sys.stdout.flush()
            sys.stderr.flush()

    def Ai(self):
        try:
            print("AI Mode wird gestartet...")
            self.Initialize()
            print("AI Mode startet...")
            self.yoloDetector.StartStreaming()
            self.modeManager.SetMode("automatic")
            while True:
                time.sleep(1) 

        except KeyboardInterrupt:
            print("Beendet durch Benutzer")
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")#
            traceback.print_exc() # Get more details about the error
        finally:
            self.lineFollower.Stop()
            self.motorLeft.SetSpeedPercent(0)
            self.motorRight.SetSpeedPercent(0)
            self.i2c.Close()
            sys.stdout.flush()
            sys.stderr.flush()

    def SayIP(self):
        ip = self.GetIp()
        while not self.websocketServer.clientConnected.is_set():
            try:
                # Divide IPs into groups of three to check for client connection in between.
                ipArray = [octet + '.' if i < len(ip.split('.')) - 1 else octet 
                for i, octet in enumerate(ip.split('.'))]

                Speaker.Speak(f"Die IP lautet {ipArray[0].replace('.', ' Punkt ')}")
                if self.websocketServer.clientConnected.is_set():
                    break
                for i in range (1,4):
                    Speaker.Speak(f"{ipArray[i].replace('.', ' Punkt ')}")
                    if self.websocketServer.clientConnected.is_set():
                        break
                
            except Exception as e:
                print(f"Error during IP announcement: {e}")


    def Run(self):
        try:
            ip = self.GetIp()
            print(f"\033[1;32m----- IP: {ip}----- \033[0m")
            self.Initialize()
            self.modeManager.SetMode("none")

            # Start IP announcement in a separate thread
            threading.Thread(target=self.SayIP, daemon=True).start()

            # Keep main thread alive for WebSocket server and other tasks
            while True:
                time.sleep(1)

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
        except KeyboardInterrupt:
            print("Program terminated by user")


        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc() # Get more details about the error
        except KeyboardInterrupt:
            print("Program terminated by user")

        finally:
            self.lineFollower.Stop()
            self.aiCommandHandler.Stop()
            self.motorLeft.SetSpeedPercent(0)
            self.motorRight.SetSpeedPercent(0)
            self.i2c.Close()
            self.cameraManager.Stop()
            self.battery.StopMonitoring()
            sys.stdout.flush()
            sys.stderr.flush()

if __name__ == '__main__':
    # Runs Tests when test is written behind main.py on the command line
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        Main().Test()
    elif len(sys.argv) > 1 and sys.argv[1] == 'line':
        Main().Line()
    elif len(sys.argv) > 1 and sys.argv[1] == 'ai':
        Main().Ai()
    else:
        Main().Run()
 