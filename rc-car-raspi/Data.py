class Data:
    # I2C Communication Configuration
    I2C = {
        "Address": 0x14,  # I2C address of the Robot HAT V4 MCU
    }

    # PWM/Timer Configuration
    Pwm = {
        "Timer": 0,               # Timer used for PWM output (0 for channels P0–P3)
        "Resolution": 4095,       # 12-bit PWM resolution (0–4095)
        "ServoFrequencyHz": 50,   # Standard servo frequency in Hz
    }

    # Hardware Register Addresses for PWM Control
    Registers = {
        "AutoReloadRegister": 0x44,  # Auto-reload register (ARR) for PWM period
        "Prescaler": 0x40,           # Prescaler register (PSC) for PWM clock division
        "ChannelBase": 0x20,         # Base address for PWM channel registers
    }

    # Motor Channel I2C Register Addresses
    Motors = {
        "Left": 0x2D,   # I2C register address for left motor control
        "Right": 0x2C,  # I2C register address for right motor control
    }

    # Servo Ranges
    ServoRanges = {
        "0": {"min": 10, "max": 120},  # Range for servo pin 0
        "1": {"min": 10, "max": 140},  # Range for servo pin 1
        "2": {"min": 50, "max": 120},  # Range for servo pin 2
    }

    # ADC
    ADC = {
        "1": 0x17,  # ADC register address for sensor 0
        "2": 0x16,  # ADC register address for sensor 1
        "3": 0x15,  # ADC register address for sensor 2
    }

    # Ultrasonic Sensor 
    UltrasonicSensor = {
        "TriggerPin": 27,  # GPIO pin for triggering the ultrasonic sensor
        "EchoPin": 22,     # GPIO pin for receiving the echo from the ultrasonic sensor
    }