from Data import Data

class GrayscaleSensor:
    def __init__(self, i2c):
        self.i2c = i2c

    
    def ReadGrayscalePercent(self, sensorNumber):
        value = self.ReadGrayscale(sensorNumber)
        value = max(0, min(value, 1500)) # Range from 0 to 1500
        value = (value / 1500) * 100  # Convert to percentage
        value = round(value, 2)  
        return value

    def ReadAverageGrayscalePercent(self):
        average = self.ReadAverageGrayscale()
        average = max(0, min(average, 1500)) # Range from 0 to 1500
        average = (average / 1500) * 100  # Convert to percentage
        average = round(average, 2)  
        return average

    def ReadGrayscale(self, sensorNumber):
        if str(sensorNumber) not in Data.ADC:
            raise ValueError(f"Sensor number {sensorNumber} does not exist.")
        else:
            register = Data.ADC[str(sensorNumber)]
        return self.i2c.ReadADC(register)

    def ReadAverageGrayscale(self):
        keys = list(Data.ADC.keys())
        average = 0
        for key in keys:
            register = Data.ADC[key]
            sensorValue = self.i2c.ReadADC(register)
            average += sensorValue
        average /= len(keys)
        return average

