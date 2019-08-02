import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import pigpio
class Windmills():

    DRIVE_FREQUENCY = 4 #Hz
    DRIVE_POSITIVE_PIN = 1
    DRIVE_NEGATIVE_PIN = 7
    BLOW_THRESHOLD_VOLTAGE = 2.0

    #adc channels passed in as list
    def __init__(self, pigpioHandle, adcHandle):
        self.pi = pigpioHandle
        self.pi.set_mode(Windmills.DRIVE_POSITIVE_PIN, pigpio.OUTPUT)
        self.pi.set_mode(Windmills.DRIVE_NEGATIVE_PIN, pigpio.OUTPUT)

        self.driveWindmills = False
        self.timeOfLastChange = 0
        self.halfPeriod = 1000/Windmills.DRIVE_FREQUENCY

        self.windmill1 = AnalogIn(adcHandle, MCP.P1)
        self.windmill2 = AnalogIn(adcHandle, MCP.P2)
        self.windmill3 = AnalogIn(adcHandle, MCP.P3)
        self.windmill4 = AnalogIn(adcHandle, MCP.P4)
        self.windmill5 = AnalogIn(adcHandle, MCP.P5)

    def numWindmillsBlown(self):
        numWindmillsBlown = 0
        if self.windmill1.voltage > self.BLOW_THRESHOLD_VOLTAGE:
            numWindmillsBlown += 1

        if self.windmill2.voltage > self.BLOW_THRESHOLD_VOLTAGE:
            numWindmillsBlown += 1

        if self.windmill3.voltage > self.BLOW_THRESHOLD_VOLTAGE:
            numWindmillsBlown += 1

        if self.windmill4.voltage > self.BLOW_THRESHOLD_VOLTAGE:
            numWindmillsBlown += 1

        if self.windmill5.voltage > self.BLOW_THRESHOLD_VOLTAGE:
            numWindmillsBlown += 1
        
        return numWindmillsBlown

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

    def areWindmillsOn(self):
        return self.driveWindmills

    def update(self, currentTime):       
        if self.driveWindmills:
            timeElapsed = currentTime - self.timeOfLastChange
            print("Windmill Time Elapsed", timeElapsed)

            if timeElapsed >= self.halfPeriod:
                if self.positivePinOn:
                    self.pi.write(Windmills.DRIVE_POSITIVE_PIN, 0)
                    self.pi.write(Windmills.DRIVE_NEGATIVE_PIN, 1)
                    self.positivePinOn = False
                else:
                    self.pi.write(Windmills.DRIVE_POSITIVE_PIN, 1)
                    self.pi.write(Windmills.DRIVE_NEGATIVE_PIN, 0)
                    self.positivePinOn = True
                    
                self.timeOfLastChange = currentTime

        else:
            self.pi.write(Windmills.DRIVE_POSITIVE_PIN, 0)
            self.pi.write(Windmills.DRIVE_NEGATIVE_PIN, 0)     

                      