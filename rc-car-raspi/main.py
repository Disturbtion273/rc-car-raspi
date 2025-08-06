#!/usr/bin/env python3

import RPi.GPIO as GPIO
from I2C import I2C
from PWM import PWM
from Motor import Motor  # Assuming Motor class is defined in Motor.py
from Data import Data  # Assuming Data class is defined in Data.py
from Servo import Servo  # Assuming Servo class is defined in Servo.py
import time

class Main:

    def run(self):
        
        self.i2c = I2C()
        self.pwm = PWM(self.i2c)
        self.motorLeft = Motor(self.pwm, directionPin=23, pwmChannel=Data.Motors["Left"], motorNumber=1)
        self.motorRight = Motor(self.pwm, directionPin=24, pwmChannel=Data.Motors["Right"], motorNumber=2)
        self.servo = Servo(self.i2c, 2)

        try:
            self.motorLeft.SetSpeedPercent(0)
            self.motorRight.SetSpeedPercent(0)
            time.sleep(1)

            print("Servo-Test beginnt...")
            self.servo.SetAnglePercent(0)
            time.sleep(1)
            self.servo.SetAnglePercent(100)
            
            print("Servo-Test abgeschlossen.")
            time.sleep(5)
            print("Vorwärts")
            for i in range(0, 101, 20):
                self.motorLeft.SetSpeedPercent(i)
                self.motorRight.SetSpeedPercent(i)
                time.sleep(1)
        except KeyboardInterrupt:
            print("Beendet durch Benutzer")
        finally:
            self.motorLeft.SetSpeedPercent(0)
            self.motorRight.SetSpeedPercent(0)
            GPIO.cleanup()
            self.i2c.Close()
        """
        try:
            pwm.setup()
            while True:
                for angle in range(110, 180, 5):
                    pwm.set_servo_angle(angle)
                    time.sleep(0.05)
                for angle in range(180, 110, -5):
                    pwm.set_servo_angle(angle)
                    time.sleep(0.05)
        except KeyboardInterrupt:
            print("Beendet durch Benutzer")
        finally:
            i2c.close()
        """

if __name__ == '__main__':
    Main().run()
