import time
import values

class InteractiveMode():

    def __init__(self, window, board):
        self.window = window
        self.board = board

        currentSolarPanelVoltage = board.getSolarPanelVoltage()
        self.PV_THRESHOLD = currentSolarPanelVoltage + 0.01
        self.WINDMILL_THRESHOLD = 2.0

        self.PV_GENERATION_UNIT = 4
        self.WINDMILL_GENERATION_UNIT = 2

        self.CITY_CONSUMPTION_1_BLOCK = 4
        self.CITY_CONSUMPTION_ADDITIONAL_BLOCK = 1.5

        self.currentBatteryLevel = 0
        self.previousBatteryLevel = 0
        

    def interactiveModeLoop(self):
        print("Starting interactive mode loop")
        self.board.stopWindmills()
        self.currentBatteryLevel = 0
        self.previousBatteryLevel = 0

        powerAvailableToConsume = 0
        lightBlock1 = False
        lightBlock2 = False
        lightBlock3 = False

        while self.window.getTaskRunning():
            self.previousBatteryLevel = self.currentBatteryLevel

            if self.areSolarPanelsOn():
                powerAvailableToConsume += self.PV_GENERATION_UNIT

            powerAvailableToConsume += self.WINDMILL_GENERATION_UNIT * self.getWindmillsBlown()

            lightBlock1, powerAvailableToConsume = self.usePower(powerAvailableToConsume, self.CITY_CONSUMPTION_1_BLOCK)
            lightBlock2, powerAvailableToConsume = self.usePower(powerAvailableToConsume, self.CITY_CONSUMPTION_ADDITIONAL_BLOCK)
            lightBlock3, powerAvailableToConsume = self.usePower(powerAvailableToConsume, self.CITY_CONSUMPTION_ADDITIONAL_BLOCK)


            if powerAvailableToConsume > 0 :
                self.storeEnergy(powerAvailableToConsume)

            self.animateBattery()
            self.animateReservoir()
            self.animateCityLights(lightBlock1, lightBlock2, lightBlock3)
            print("Battery level: " + str(self.currentBatteryLevel))
            time.sleep(1)

        self.board.resetBoard()
        
    
    def areSolarPanelsOn(self):
        solarPanelVoltage = self.board.getSolarPanelVoltage()
        print(solarPanelVoltage)

        if solarPanelVoltage >= self.PV_THRESHOLD:
            print("Solar panels on")
            return True
        else:
            print("Solar panels off")
            return False

    def getWindmillsBlown(self):
        windmillsBlown = 0
        windmillVoltages = self.board.getWindmillVoltages()

        for i in range(len(windmillVoltages)):
            if windmillVoltages[i] >= self.WINDMILL_THRESHOLD:
                print("Windmill " + str(i) + " Running")
                windmillsBlown += 1
            else:
                print("Windmill " + str(i) + " stopped")

        return windmillsBlown

    def animateBattery(self):
        batteryLevelChange = self.currentBatteryLevel - self.previousBatteryLevel

        #charging
        if batteryLevelChange > 0:
            batteryLEDcolour = (int(values.LED_BLUE_MAX[0] * (self.currentBatteryLevel/100)),
            int(values.LED_BLUE_MAX[1] * (self.currentBatteryLevel/100)),
            int(values.LED_BLUE_MAX[2] * (self.currentBatteryLevel/100)))

            self.board.setFuelCellLEDs(batteryLEDcolour)
            self.board.pulseFuelCell()
        elif batteryLevelChange < 0:
            #discharging
            batteryLEDcolour = (int(values.LED_YELLOW_MAX[0] * (self.currentBatteryLevel/100)),
            int((values.LED_YELLOW_MAX[1] * (self.currentBatteryLevel/100))),
            int((values.LED_YELLOW_MAX[2] * (self.currentBatteryLevel/100))))

            self.board.setFuelCellLEDs(batteryLEDcolour)
        elif  batteryLevelChange == 0:
            if self.currentBatteryLevel == 0:
                self.board.setFuelCellLEDs(values.LED_RED_DIM)
            elif self.currentBatteryLevel == 100:
                self.board.setFuelCellLEDs(values.LED_GREEN_BRIGHT)
        
    def animateReservoir(self):
        if self.currentBatteryLevel == 0:
            level0Colour = (0,0,0)
            level1Colour = (0,0,0)
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif self.currentBatteryLevel > 0 and self.currentBatteryLevel < 25:
            level0Colour = values.LED_WATER_BLUE
            level1Colour = (0,0,0)
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif self.currentBatteryLevel >= 25 and self.currentBatteryLevel < 50:
            level0Colour = values.LED_WATER_BLUE
            level1Colour = values.LED_WATER_BLUE
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif self.currentBatteryLevel >= 50 and self.currentBatteryLevel < 75:
            level0Colour = values.LED_WATER_BLUE
            level1Colour = values.LED_WATER_BLUE
            level2Colour = values.LED_WATER_BLUE
            level3Colour = (0,0,0)
        elif self.currentBatteryLevel >= 75:
            level0Colour = values.LED_WATER_BLUE
            level1Colour = values.LED_WATER_BLUE
            level2Colour = values.LED_WATER_BLUE
            level3Colour = values.LED_WATER_BLUE

        self.board.setReservoirLEDs(level0Colour,level1Colour,level2Colour,level3Colour)


    def animateCityLights(self, lightBlock1, lightBlock2, lightBlock3):
        cityLightsCoefficient = 0.0

        if lightBlock1:
            cityLightsCoefficient += 0.33

        if lightBlock2:
            cityLightsCoefficient += 0.33

        if lightBlock3:
            cityLightsCoefficient += 0.33

        self.board.lightCityBlocks(cityLightsCoefficient)


    def usePower(self, powerAvailable, powerConsumed):
        newPower = powerAvailable - powerConsumed
        sufficientPower = True
        if newPower < 0:
            self.currentBatteryLevel  = self.currentBatteryLevel + newPower #newPower is negative, representing power deficiency 
            if self.currentBatteryLevel < 0:
                self.currentBatteryLevel = 0                
                sufficientPower = False

            newPower = 0

        return sufficientPower, newPower

    def storeEnergy(self, energyToStore):
        self.currentBatteryLevel += energyToStore

        if self.currentBatteryLevel > 100:
            self.currentBatteryLevel = 100
