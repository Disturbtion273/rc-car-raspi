import RPi.GPIO as GPIO
import time
from I2C import I2C
from PWM import PWM
from Motor import Motor

class Main:
    def __init__(self):
        self.i2c = I2C()
        self.pwm = PWM(self.i2c)
        self.motorLeft = Motor(self.pwm, directionPin=23, pwmChannel=self.pwm.Motor1Channel, motorNumber=1)
        self.motorRight = Motor(self.pwm, directionPin=24, pwmChannel=self.pwm.Motor2Channel, motorNumber=2)

    def Run(self):
        try:
            print("Initialisiere PWM-Timer...")
            self.pwm.InitializeTimer(frequency=50)

            self.motorLeft.SetSpeedPercent(0)
            self.motorRight.SetSpeedPercent(0)
            time.sleep(3)
            
            print("Vorwärts")
            for i in range(0, 101, 20):
                self.motorLeft.SetSpeedPercent(i)
                self.motorRight.SetSpeedPercent(i)
                time.sleep(1)

            self.motorLeft.Stop()
            self.motorRight.Stop()
            time.sleep(1)
            
            print("Rückwärts")
            self.motorLeft.SetSpeedPercent(-100)
            self.motorRight.SetSpeedPercent(-100)
            time.sleep(2)

            for i in range(-100, 1, 20):
                self.motorLeft.SetSpeedPercent(i)
                self.motorRight.SetSpeedPercent(i)
                time.sleep(1)

            print("Stoppe Motoren")
            self.motorLeft.Stop()
            self.motorRight.Stop()

        except Exception as e:
            print(f"Fehler: {e}")
            self.motorLeft.Stop()
            self.motorRight.Stop()
        finally:
            GPIO.cleanup()
            self.i2c.Close()

if __name__ == "__main__":
    main = Main()
    main.Run()
