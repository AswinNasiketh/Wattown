from adafruit_mcp3xxx.analog_in import AnalogIn
import adafruit_mcp3xxx.mcp3008 as MCP

class SolarPanels():

    def __init__(self, adcHandle):
        self.solarPanelADC = AnalogIn(adcHandle, MCP.P7)
        self.PV_THRESHOLD_VOLTAGE = self.solarPanelADC.voltage + 0.1

    def areSolarPanelsOn(self):
        return (self.solarPanelADC.voltage > self.PV_THRESHOLD_VOLTAGE)

    def resetThreshold(self):
        self.PV_THRESHOLD_VOLTAGE = self.solarPanelADC.voltage + 0.1
            