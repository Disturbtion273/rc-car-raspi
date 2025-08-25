from Data import Data
from I2C import I2C

class BatteryVoltage:
    """
    Liest die Batteriespannung über I2C-ADC und berechnet die echte Batteriespannung.
    """

    def __init__(self, i2c: I2C, voltage_divider_ratio: float = 2.24):
        self.i2c = i2c
        self.adc_channel = Data.ADC["Battery"]  # ADC-Kanal laut Konfiguration
        self.voltage_divider_ratio = voltage_divider_ratio
        self.reference_voltage = 3.3
        self.adc_resolution = 4095  # 12-Bit-ADC

    def _read_adc_raw(self):
        reg = 0x10 + (7 - self.adc_channel)
        self.i2c.write([reg, 0, 0])
        raw_bytes = self.i2c.bus.read_i2c_block_data(self.i2c.address, reg, 2)
        msb, lsb = raw_bytes[0], raw_bytes[1]
        raw_value = (msb << 8) + lsb
        return raw_value

    def get_voltage(self) -> float:
        raw_adc = self._read_adc_raw()
        voltage_at_adc = (raw_adc / self.adc_resolution) * self.reference_voltage
        battery_voltage = voltage_at_adc * self.voltage_divider_ratio
        print(f"Raw ADC Value: {raw_adc}")
        print(f"Voltage at ADC: {voltage_at_adc:.2f} V")
        print(f"Battery Voltage: {battery_voltage:.2f} V")
        return battery_voltage

    def get_percentage(self, min_voltage=6.6, max_voltage=8.4) -> float:
        voltage = self.get_voltage()
        percentage = (voltage - min_voltage) / (max_voltage - min_voltage) * 100
        return max(0, min(100, percentage))
