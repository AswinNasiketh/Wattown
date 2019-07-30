from values import *
import pigpio

class FuelCell():

    #TODO: change LED addresses to include added transmission network and distribution network LEDs

    PULSE_PERIOD = 500 #ms
    FUEL_CELL_PIN = 8

    LED_FUEL_CELL_RANGE_LOWER = 112
    LED_FUEL_CELL_RANGE_UPPER = 113 

    def __init__(self, LEDHandle, pigpioHandle):
        self.LEDHandle = LEDHandle
        self.pi = pigpioHandle
        self.pi.set_mode(FuelCell.FUEL_CELL_PIN, pigpio.OUTPUT)

        self.pulse = False
        self.pinOn = False
        self.timeOfLastChange = 0

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
                batteryLEDColour = [int(LED_BLUE_MAX[i] * brightnessCoefficient) for i in range(3)]
            else:
                batteryLEDColour = [int(LED_YELLOW_MAX[i] * brightnessCoefficient) for i in range(3)]

            batteryLEDColour = tuple(batteryLEDColour)
        else:
            if energyLevel == 0:
                batteryLEDColour = LED_RED_DIM
            else:
                batteryLEDColour = LED_GREEN_BRIGHT
        
        for i in range(FuelCell.LED_FUEL_CELL_RANGE_LOWER, FuelCell.LED_FUEL_CELL_RANGE_UPPER + 1):
            self.LEDHandle[i] = batteryLEDColour
        

    
    def update(self, currentTime):
        if self.pulse:
            timeElapsed = currentTime - self.timeOfLastChange

            if timeElapsed >= FuelCell.PULSE_PERIOD:
                if self.pinOn:
                    self.pi.write(FuelCell.FUEL_CELL_PIN, 0)
                    self.pinOn = False
                    self.pulse = False
                else:
                    self.pi.write(FuelCell.FUEL_CELL_PIN, 1)
                    self.pinOn = True
                
                self.timeOfLastChange = currentTime

        else:
            self.pi.write(FuelCell.FUEL_CELL_PIN, 0)

        