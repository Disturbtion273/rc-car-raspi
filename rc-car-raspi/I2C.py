import smbus2
from Data import Data

class I2C:
    """
    A class to handle I2C communication using the smbus2 library.
    """

    def __init__(self, address=Data.I2C["Address"], busNumber=1):
        """
        Initialize the I2C object with a specific device address and bus number.

        :param address: The I2C address of the target device.
        :type address: int
        :param busNumber: The I2C bus number (usually 1 on Raspberry Pi).
        :type busNumber: int
        """
        self.address = address
        self.bus = smbus2.SMBus(busNumber)

    def WriteWordData(self, register, value):
        """
        Write a 16-bit word to a specific register of the I2C device.

        :param register: The target register in the I2C device.
        :type register: int
        :param value: The 16-bit word to write.
        :type value: int
        """
        msb = (value >> 8) & 0xFF
        lsb = value & 0xFF
        value = (lsb << 8) + msb
        self.bus.write_word_data(self.address, register, value)

    def WriteRegister(self, register, value):
        """
        Write a 16-bit value to a register using I2C block data.

        :param register: The register address to write to.
        :type register: int
        :param value: The 16-bit value to write.
        :type value: int
        """
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        self.bus.write_i2c_block_data(self.address, register, [high_byte, low_byte])

    def ReadADC(self, register):
        """
        Read a 16-bit value from an ADC register.

        :param register: The register address to read from.
        :type register: int
        :return: The 16-bit ADC value.
        :rtype: int
        """
        self.bus.write_word_data(self.address, register, 0x0000)
        msb = self.bus.read_byte(self.address)
        lsb = self.bus.read_byte(self.address)
        value = (msb << 8) | lsb
        return value

    def Close(self):
        """
        Close the I2C bus connection to release system resources.
        """
        self.bus.close()