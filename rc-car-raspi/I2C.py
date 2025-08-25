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

    def write(self, data):
        """
        Write data to the I2C device

        :param data: Data to write (int, list, or bytearray)
        :raises: ValueError if data type is unsupported
        """
        if isinstance(data, bytearray):
            data_all = list(data)
        elif isinstance(data, int):
            if data == 0:
                data_all = [0]
            else:
                data_all = []
                while data > 0:
                    data_all.append(data & 0xFF)
                    data >>= 8
        elif isinstance(data, list):
            data_all = data
        else:
            raise ValueError(
                f"write data must be int, list, or bytearray, not {type(data)}"
            )

        # Write data
        if len(data_all) == 1:
            data = data_all[0]
            self._write_byte(data)
        elif len(data_all) == 2:
            reg = data_all[0]
            data = data_all[1]
            self._write_byte_data(reg, data)
        elif len(data_all) == 3:
            reg = data_all[0]
            data = (data_all[2] << 8) + data_all[1]
            self._write_word_data(reg, data)
        else:
            reg = data_all[0]
            data = list(data_all[1:])
            self._write_i2c_block_data(reg, data)

    # Internal helper methods
    def _write_byte(self, value):
        self.bus.write_byte(self.address, value)

    def _write_byte_data(self, register, value):
        self.bus.write_byte_data(self.address, register, value)

    def _write_word_data(self, register, value):
        self.bus.write_word_data(self.address, register, value)

    def _write_i2c_block_data(self, register, data):
        self.bus.write_i2c_block_data(self.address, register, data)

    def Close(self):
        """
        Close the I2C bus connection to release system resources.
        """
        self.bus.close()