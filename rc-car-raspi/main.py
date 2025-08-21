#!/usr/bin/env python3

import time
import sys
import socket
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

class Main:
    def InitializeHardware(self):
        self.i2c = I2C()
        self.pwm = PWM(self.i2c)
        self.motorLeft = Motor(self.pwm, motorNumber=1)
        self.motorRight = Motor(self.pwm, motorNumber=2)
        self.servoTilt = Servo(self.pwm, 0)
        self.servoPan = Servo(self.pwm, 1)
        self.servoSteering = Servo(self.pwm, 2)
        self.grayscaleSensor = GrayscaleSensor(self.i2c)
        self.ultrasonicSensor = UltrasonicSensor()

        self.servoSteering.SetAnglePercent(50)  
        self.servoTilt.SetAnglePercent(50)      
        self.servoPan.SetAnglePercent(50)       
        
    def StartWebsocketServer(self):
        websocketCommandHandler = WebsocketCommandHandler(self.motorLeft, self.motorRight, self.servoTilt, self.servoPan, self.servoSteering)
        websocketServer = WebsocketServer(websocketCommandHandler)
        websocketServer.Start("0.0.0.0", 9999)

    def getIp(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("192.168.0.1", 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            return f"Fehler: {e}"


    def Test(self):
        self.InitializeHardware()
        self.StartWebsocketServer()

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

    def run(self):
        try:
            ip = self.getIp()
            print(f"\033[1;32m----- IP: {ip}----- \033[0m")
            self.InitializeHardware()
            print(f"\033[1;32mStart Websocket\033[0m")
            self.StartWebsocketServer()
            print(f"\033[1;32mStart Camera Stream\033[0m")
            self.cameraStream = CameraStream()
            self.cameraStream.start()  
            print(f"\033[1;32mEverything is running.\033[0m")

            while True:
                time.sleep(1) # Keep the main thread alive to allow WebSocket server to run

        except Exception as e:
            print(f"An error occurred: {e}")

        except KeyboardInterrupt:
            print("Program terminated by user")

        finally:
            self.motorLeft.SetSpeedPercent(0)
            self.motorRight.SetSpeedPercent(0)
            self.motorLeft.Cleanup()
            self.motorRight.Cleanup()
            self.cameraStream.stop()
            self.i2c.Close()

if __name__ == '__main__':
    # Runs Tests when test is written behind main.py on the command line
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        Main().Test()
    else:
        Main().run()
