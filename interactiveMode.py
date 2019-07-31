import time
import values
import threading

class InteractiveModeThread(threading.Thread):

    def __init__(self, board):
        self.interactiveModeObj = InteractiveMode(board)
        self.stopEvent = threading.Event()
        board.resetBoard()
        threading.Thread.__init__(self)

    def run(self):
        self.stopEvent.clear()
        while not self.stopEvent.is_set():
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
        print("Battery level: " + str(self.currentBatteryLevel))
        time.sleep(1)
        

    def getWindmillsBlown(self):
        windmillsBlown = 0
        windmillVoltages = self.board.windmills.getWindmillVoltages()

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

        self.cityPoweredPercent = round(cityLightsCoefficient * 100)

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
        return self.cityPoweredPercent