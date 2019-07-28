import time
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

class Windmills():

    DRIVE_FREQUENCY = 4 #Hz
    DRIVE_POSITIVE_PIN = 1
    DRIVE_NEGATIVE_PIN = 7

    #adc channels passed in as list
    def __init__(self, pigpioHandle, adcHandle):
        self.pi = pigpioHandle
        self.driveWindmills = False
        self.timeSinceLastUpdate = self.getTimeMilliseconds()
        self.halfPeriod = 1000/DRIVE_FREQUENCY

        self.windmill1 = AnalogIn(adcHandle, MCP.P1)
        self.windmill2 = AnalogIn(adcHandle, MCP.P2)
        self.windmill3 = AnalogIn(adcHandle, MCP.P3)
        self.windmill4 = AnalogIn(adcHandle, MCP.P4)
        self.windmill5 = AnalogIn(adcHandle, MCP.P5)

    def getWindmillVoltages(self):
        return [self.windmill1.voltage,
        self.windmill2.voltage,
        self.windmill3.voltage,
        self.windmill4.voltage,
        self.windmill5.voltage]

    def startWindmills(self):
        self.driveWindmills = True
        self.positivePinOn = False

    def stopWindmills(self):
        self.driveWindmills = False

    def update(self):       
        if self.driveWindmills:
            timeElapsed = getTimeMilliseconds() - self.timeSinceLastUpdate


            if timeElapsed >= self.halfPeriod:
                if self.positivePinOn:
                    self.pi.write(DRIVE_POSITIVE_PIN, 0)
                    self.pi.write(DRIVE_NEGATIVE_PIN, 1)
                    self.positivePinOn = False
                else:
                    self.pi.write(DRIVE_POSITIVE_PIN, 1)
                    self.pi.write(DRIVE_NEGATIVE_PIN, 0)
                    self.positivePinOn = True

        else:
            self.pi.write(DRIVE_POSITIVE_PIN, 0)
            self.pi.write(DRIVE_NEGATIVE_PIN, 0)     

        self.timeSinceLastUpdate = getTimeMilliseconds()              

    def getTimeMilliseconds(self):
        return int(round(time.time() * 1000))