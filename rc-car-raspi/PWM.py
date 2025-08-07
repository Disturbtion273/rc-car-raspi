from Data import Data

class PWM:    
    def __init__(self, i2c):
        self.i2c = i2c
        self.pwmFreq = Data.Pwm["ServoFrequencyHz"]
        self.resolution = Data.Pwm["Resolution"]
        self.timer = Data.Pwm["Timer"]
        self.prescaler = Data.Registers["Prescaler"]
        self.arr = Data.Registers["AutoReloadRegister"]
        self.Setup()

    def Setup(self):
        # Set auto-reload register (ARR) to PWM resolution (max count value)
        self.i2c.WriteWordData(self.arr + self.timer, self.resolution) 

        # Calculate prescaler value to get desired PWM frequency based on 72 MHz clock
        prescaler = int(72000000 / (self.resolution + 1) / self.pwmFreq) - 1

        # Write prescaler value to prescaler register
        self.i2c.WriteWordData(self.prescaler + self.timer, prescaler)

    def SetMotorPwm(self, channel, speed):
        value = max(0, min(speed, 4095))
        self.i2c.WriteWordData(channel, value)

    def SetServoPwm(self, pin, value, min_us=500, max_us=2500):
        # Convert the angle value (0–180°) to a pulse width in microseconds
        pulse_us = min_us + (value / 180.0) * (max_us - min_us)

        # Calculate the PWM period in microseconds based on servo frequency
        period_us = 1e6 / Data.Pwm["ServoFrequencyHz"]

        # Calculate duty cycle as a fraction (0 to 1)
        dutyCycle = pulse_us / period_us

        # Convert duty cycle to a pulse value based on PWM resolution
        pulse = int(dutyCycle * Data.Pwm["Resolution"])

        # Write the pulse value to the corresponding PWM channel register
        self.i2c.WriteRegister(Data.Registers["ChannelBase"] + pin, pulse)
        
