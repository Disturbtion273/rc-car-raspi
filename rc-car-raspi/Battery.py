import time
import threading
from Data import Data
from I2C import I2C

class Battery:
    """
    Class to handle battery voltage and percentage reading via I2C ADC.
    Runs a background thread to check battery status every 30 seconds.
    """

    def __init__(self, i2c: I2C, updateInterval=30):
        self.i2c = i2c
        self.batteryRegister = 0x13  # Register für Batterie-ADC
        self.updateInterval = updateInterval
        self.isMonitoring = False
        self.thread = None

    def GetVoltage(self):
        """
        Reads the battery voltage in Volts.
        :return: Voltage (float)
        """
        rawValue = self.i2c.ReadADC(self.batteryRegister)
        voltage = rawValue / 4095.0 * 3.3 * 3  # Formel aus SunFounder-Doku
        return voltage

    def GetPercentage(self):
        """
        Converts the battery voltage into percentage.
        Assumes: 6.0V = 0%, 8.4V = 100%
        :return: (percent, voltage)
        """
        voltage = self.GetVoltage()
        percent = (voltage - 6.0) / (8.4 - 6.0) * 100
        percent = max(0, min(100, percent))  # Clamp 0–100%
        return percent, voltage

    def MonitorLoop(self):
        """
        Private loop for periodic monitoring.
        """
        while self.isMonitoring:
            percent, voltage = self.GetPercentage()
            print(f"Battery: {percent:.1f}% ({voltage:.2f} V)")
            time.sleep(self.updateInterval)

    def StartMonitoring(self):
        """
        Starts the monitoring thread.
        """
        if not self.isMonitoring:
            self.isMonitoring = True
            self.thread = threading.Thread(target=self.MonitorLoop, daemon=True)
            self.thread.start()

    def StopMonitoring(self):
        """
        Stops the monitoring thread.
        """
        self.isMonitoring = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

