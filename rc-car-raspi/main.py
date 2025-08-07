#!/usr/bin/env python3

import RPi.GPIO as GPIO
from I2C import I2C
from PWM import PWM
from Motor import Motor  
from Data import Data  
from Servo import Servo 
from GrayscaleSensor import GrayscaleSensor  
from UltrasonicSensor import UltrasonicSensor
import time

class Main:

    def run(self):
        
        self.i2c = I2C()
        self.pwm = PWM(self.i2c)
        self.motorLeft = Motor(self.pwm, directionPin=23, pwmChannel=Data.Motors["Left"], motorNumber=1)
        self.motorRight = Motor(self.pwm, directionPin=24, pwmChannel=Data.Motors["Right"], motorNumber=2)
        self.servo = Servo(self.pwm, 0)
        self.grayscaleSensor = GrayscaleSensor(self.i2c)
        self.ultrasonicSensor = UltrasonicSensor()

        try:
            self.motorLeft.SetSpeedPercent(0)
            self.motorRight.SetSpeedPercent(0)
            time.sleep(1)
            print("----Start Test:----")
            print("Ultrasonic-Sensor-Test beginnt...")
            for i in range(10):
                distance = self.ultrasonicSensor.GetDistance()
                print(f"Entfernung: {distance:.2f} cm")
                time.sleep(0.5)

            print("Grayscale-Sensor-Test beginnt...")
            for i in range(10):
                sensor_value = self.grayscaleSensor.ReadGrayscalePercent(1)
                print(f"Sensor 1 Wert: {sensor_value}")
                sensor_value = self.grayscaleSensor.ReadGrayscalePercent(2)
                print(f"Sensor 2 Wert: {sensor_value}")
                sensor_value = self.grayscaleSensor.ReadGrayscalePercent(3)
                print(f"Sensor 3 Wert: {sensor_value}")
                average_value = self.grayscaleSensor.ReadAverageGrayscalePercent()
                print(f"Durchschnittswert: {average_value}")
                time.sleep(0.5)

            print("Servo-Test beginnt...")
            self.servo.SetAnglePercent(0)
            time.sleep(1)
            self.servo.SetAnglePercent(100)
            
            time.sleep(5)
            print("Vorwärts")
            for i in range(0, 101, 20):
                self.motorLeft.SetSpeedPercent(i)
                self.motorRight.SetSpeedPercent(i)
                time.sleep(1)
            print("Rückwärts")
            for i in range(100, -1, -20):
                self.motorLeft.SetSpeedPercent(-i)
                self.motorRight.SetSpeedPercent(-i)
                time.sleep(1)

        except KeyboardInterrupt:
            print("Beendet durch Benutzer")
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
        finally:
            self.motorLeft.SetSpeedPercent(0)
            self.motorRight.SetSpeedPercent(0)
            GPIO.cleanup()
            self.i2c.Close()

if __name__ == '__main__':
    Main().run()
