import time
import subprocess
import Adafruit_MCP3008

class Signal:
    def __init__(self):
        self.signalStrength = 0
        self.signalQuality = 0
        self.getData()

    def getData(self):
        output = subprocess.check_output("iwconfig wlan0 | grep -i quality", shell=True).decode().split(" ")
        self.signalQuality = output[11].split("=")[1]


class Battery:

    MAX_MCP_READ = 1023
    BATTERY_MAX_VOLTAGE = 8.4
    BATTERY_MIN_VOLTAGE = 6.0
    BATTERY_LOW_VOLTAGE = 7.2
    BATTERY_CRITICAL_VOLTAGE = 6.4
    BATTERY_DIFF_VOLTAGE = BATTERY_MAX_VOLTAGE - BATTERY_MIN_VOLTAGE

    BATTERY_MIN_MCP = (MAX_MCP_READ*BATTERY_MIN_VOLTAGE)/BATTERY_MAX_VOLTAGE
    BATTERY_DIFF_MCP = MAX_MCP_READ - BATTERY_MIN_MCP

    def __init__(self):
        self.CLK = 18
        self.MISO = 17
        self.MOSI = 27
        self.CS = 22
        self.mcp = Adafruit_MCP3008.MCP3008(clk=self.CLK, cs=self.CS, miso=self.MISO, mosi=self.MOSI)
        self.battVoltage = 0
        self.battPercentage = 0
        print("Read")

    def computeBatteryLevel(self):
        # Get avg of mcp read value
        value = 0
        for i in range(10):
            value += self.mcp.read_adc(0)
            time.sleep(0.01)
        value /= 10

        self.battPercentage = (self.BATTERY_DIFF_MCP - (self.MAX_MCP_READ - value))/self.BATTERY_DIFF_MCP
        self.battVoltage = (self.BATTERY_MAX_VOLTAGE * value) / self.MAX_MCP_READ

    def printBatteryInfo(self):
        print("Battery voltage: %.2f" % self.battVoltage)
        print("Battery percentage: %.2f" % (self.battPercentage*100))
