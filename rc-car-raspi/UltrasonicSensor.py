import RPi.GPIO as GPIO
from Data import Data
import time

class UltrasonicSensor:
    def __init__(self):
        self.triggerPin = Data.UltrasonicSensor["TriggerPin"]
        self.echoPin = Data.UltrasonicSensor["EchoPin"]
        self.SetupPins()

    def SetupPins(self):
        # Setup GPIO pins for the ultrasonic sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.triggerPin, GPIO.OUT)
        GPIO.setup(self.echoPin, GPIO.IN)

    def GetDistance(self):
        # Trigger the ultrasonic sensor
        GPIO.output(self.triggerPin, True)
        time.sleep(0.00001)  # 10 microseconds
        GPIO.output(self.triggerPin, False)

        # Wait for the echo response
        startTime = time.time()
        while GPIO.input(self.echoPin) == 0:
            startTime = time.time()

        stopTime = time.time()
        while GPIO.input(self.echoPin) == 1:
            stopTime = time.time()

        # Calculate distance in cm
        elapsedTime = stopTime - startTime
        distance = (elapsedTime * 34300) / 2  # Speed of sound is 34300 cm/s

        return distance

    def cleanup(self):
        GPIO.cleanup()