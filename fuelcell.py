from utilFunctions import *
from values import *
import pigpio

class FuelCell():

    PULSE_PERIOD = 500 #ms
    FUEL_CELL_PIN = 8

    LED_FUEL_CELL_RANGE_LOWER = 99
    LED_FUEL_CELL_RANGE_UPPER = 100  

    def __init__(self, LEDHandle, pigpioHandle):
        self.LEDHandle = LEDHandle
        self.pi = pigpioHandle
        self.pi.set_mode(FuelCell.FUEL_CELL_PIN, pigpio.OUTPUT)

        self.pulse = False
        self.pinOn = False
        self.timeSinceLastUpdate = getTimeMilliseconds()

    def startPulsing(self):
        self.pulse = True
        self.pinOn = False

    def stopPulsing(self):
        self.pulse = False

    def setEnergyLevel(self, energyLevel, levelChanging, charging = False):
        brightnessCoefficient = energyLevel/100.0

        if levelChanging:
            if charging:
                self.pulse = True
                batteryLEDColour = (int(LED_BLUE_MAX[i] * brightnessCoefficient) for i in range(3))
            else:
                batteryLEDColour = (int(LED_YELLOW_MAX[i] * brightnessCoefficient) for i in range(3))
        else:
            if energyLevel == 0:
                batteryLEDColour = LED_RED_DIM
            elif energyLevel == 100:
                batteryLEDColour = LED_GREEN_BRIGHT
        
        for i in range(FuelCell.LED_FUEL_CELL_RANGE_LOWER, FuelCell.LED_FUEL_CELL_RANGE_UPPER + 1):
            self.LEDHandle[i] = batteryLEDColour
        

    
    def update(self):
        if self.pulse:
            timeElapsed = getTimeMilliseconds() - self.timeSinceLastUpdate

            if timeElapsed >= FuelCell.PULSE_PERIOD:
                if self.pinOn:
                    self.pi.write(FuelCell.FUEL_CELL_PIN, 0)
                    self.pinOn = False
                    self.pulse = False
                else:
                    self.pi.write(FuelCell.FUEL_CELL_PIN, 1)
                    self.pinOn = True

        else:
            self.pi.write(FuelCell.FUEL_CELL_PIN, 0)

        self.timeSinceLastUpdate = getTimeMilliseconds() 