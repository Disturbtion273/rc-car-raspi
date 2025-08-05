from I2C import I2C

REG_CHN_BASE = 0x20
PWM_CHANNEL = 0  # Kanal für Servo
PWM_FREQ = 50
PWM_RESOLUTION = 4095

class Servo:
    def __init__(self, i2c: I2C, channel: int = PWM_CHANNEL):
        self.i2c = i2c
        self.channel = channel

    def angle_to_pulse(self, angle: float, min_us=500, max_us=2500) -> int:
        pulse_us = min_us + (angle / 180.0) * (max_us - min_us)
        period_us = 1e6 / PWM_FREQ
        duty_cycle = pulse_us / period_us
        return int(duty_cycle * PWM_RESOLUTION)

    def set_angle(self, angle: float):
        pulse = self.angle_to_pulse(angle)
        self.i2c.write_register(REG_CHN_BASE + self.channel, pulse)
        print(f"Angle: {angle}°, Pulse: {pulse}")
