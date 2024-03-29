import threading

class InteractiveModeThread(threading.Thread):

    def __init__(self, board):
        self.interactiveModeObj = InteractiveMode(board)
        self.stopEvent = threading.Event()
        board.resetBoard()
        threading.Thread.__init__(self)

    def run(self):
        self.stopEvent.clear()
        while not self.stopEvent.wait(1):
            self.interactiveModeObj.iterateLoop()

    def join(self, timeOut=None):
        self.stopEvent.set()
        threading.Thread.join(self,timeOut)

class InteractiveMode():

    def __init__(self, board):
        self.board = board

        self.WINDMILL_THRESHOLD = 2.0

        self.PV_GENERATION_UNIT = 4
        self.WINDMILL_GENERATION_UNIT = 2

        self.CITY_CONSUMPTION_1_BLOCK = 4
        self.CITY_CONSUMPTION_ADDITIONAL_BLOCK = 1.5

        self.currentBatteryLevel = 0
        self.previousBatteryLevel = 0

        self.lightBlock1 = False
        self.lightBlock2 = False
        self.lightBlock3 = False
 
        
    def iterateLoop(self):

        powerAvailableToConsume = 0
        self.lightBlock1 = False
        self.lightBlock2 = False
        self.lightBlock3 = False

        self.previousBatteryLevel = self.currentBatteryLevel

        if self.board.solarPanels.areSolarPanelsOn():
            powerAvailableToConsume += self.PV_GENERATION_UNIT

        powerAvailableToConsume += self.WINDMILL_GENERATION_UNIT * self.getWindmillsBlown()

        self.lightBlock1, powerAvailableToConsume = self.usePower(powerAvailableToConsume, self.CITY_CONSUMPTION_1_BLOCK)
        self.lightBlock2, powerAvailableToConsume = self.usePower(powerAvailableToConsume, self.CITY_CONSUMPTION_ADDITIONAL_BLOCK)
        self.lightBlock3, powerAvailableToConsume = self.usePower(powerAvailableToConsume, self.CITY_CONSUMPTION_ADDITIONAL_BLOCK)


        if powerAvailableToConsume > 0 :
            self.storeEnergy(powerAvailableToConsume)

        self.animateBattery()
        self.animateReservoir()
        self.animateCityLights()
        self.animateTransmissionLine()
        self.animateDistributionLines()
        self.animateWattownSign()
        
        # print("Battery level: " + str(self.currentBatteryLevel))
        
    def animateWattownSign(self):
        if self.lightBlock3: #only turn on sign if there's sufficient power to turn on all of the city
            self.board.wattownSign.turnOn()
        else:
            self.board.wattownSign.turnOff()

    def animateTransmissionLine(self):
        if self.lightBlock1: #signifies some power is flowing
            self.board.transmissionLine.setAllTowersColour((50, 50, 50)) # white for in use
        else:
            self.board.transmissionLine.setAllTowersColour((58, 51, 4)) # yellow for not in use

    def animateDistributionLines(self):
        if self.lightBlock1: #signifies some power is flowing
            self.board.distributionMiddle.startPowerFlow()            
        else:
            self.board.distributionMiddle.stopPowerFlow()
        #right distribution line only comes on when city is fully powered
        if self.lightBlock3:
            self.board.distributionRight.startPowerFlow()
        else:
            self.board.distributionRight.stopPowerFlow()
    def getWindmillsBlown(self):
        windmillsBlown = self.board.windmills.numWindmillsBlown()
        return windmillsBlown

    def animateBattery(self):
        batteryLevelChange = self.currentBatteryLevel - self.previousBatteryLevel

        #charging
        if batteryLevelChange > 0:
            self.board.fuelCell.setEnergyLevel(self.currentBatteryLevel, True, True)
        elif batteryLevelChange < 0:
            #discharging
            self.board.fuelCell.setEnergyLevel(self.currentBatteryLevel, True, False)
        else:
            self.board.fuelCell.setEnergyLevel(self.currentBatteryLevel, False)
        
    def animateReservoir(self):
        self.board.lightReservoir(self.currentBatteryLevel)


    def animateCityLights(self):
        cityLightsCoefficient = 0.0

        if self.lightBlock1:
            cityLightsCoefficient += 0.33

        if self.lightBlock2:
            cityLightsCoefficient += 0.33

        if self.lightBlock3:
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

    def getCityPoweredPercent(self):
        poweredPercent = 0.0
        if self.lightBlock1:
            poweredPercent += 33.3

        if self.lightBlock2:
            poweredPercent += 33.3

        if self.lightBlock3:
            poweredPercent += 33.3

        return round(poweredPercent)