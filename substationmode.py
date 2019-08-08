from cycleSim import CycleSim
from threading import Thread, Event
import values
from substation import Substation
class SubstationModeThread(Thread):
    
    def __init__(self, board):
        self.board = board
        self.substationModeObj = SubstationMode(board)
        self.stopEvent = Event()
        board.resetBoard()
        Thread.__init__(self)
        

    def run(self):
        self.stopEvent.clear()

        while not self.stopEvent.wait(5):
            if not self.substationModeObj.getStillRunning():
                break
            self.substationModeObj.iterateLoop()
            self.board.transmissionLine.setAllTowersColour(values.LED_WHITE)

        #if the stop event isn't set, but the simulation isn't still running
        if (not self.stopEvent.is_set()) and (not self.substationModeObj.getStillRunning()):
            self.cleanUp()

    def cleanUp(self):
        self.board.resetBoard()

    def join(self, timeOut = None):
        self.stopEvent.set()  
        self.cleanUp()     
        Thread.join(self,timeOut)

    def configure(self, sustainable):
        self.substationModeObj.configure(-1, sustainable) # -1 to have simulation run forever


class SubstationMode(CycleSim):
    
    def __init__(self, board):
        super().__init__(board)

        self.switch1Closed = True # currently controls city
        self.switch2Closed = True
        self.switch3Closed = True
        self.currentConsumption = 0

    def animateCityLights(self, consumption, maxConsumption, minConsumption):
        maxConsumptionDelta = maxConsumption - minConsumption

        consumptionAboveMin = consumption - minConsumption

        cityLightsCoefficent = consumptionAboveMin/maxConsumptionDelta
        self.board.lightCityBlocks(cityLightsCoefficent, not self.switch1Closed, True)

    #returns true if there is sufficient power, otherwise false
    def consumePower(self):
        #only light up the city if we have enough capacity in the reservoir or battery
        self.reservoirPower = 0
        if self.switch1Closed:
            self.currentConsumption = self.consumptionValues[self.hourCount]
        else:
            self.currentConsumption = self.consumptionValues[self.hourCount]/2
        
        if self.subtractFromReservoir(self.currentConsumption):
            self.animateCityLights(self.consumptionValues[self.hourCount], values.MAX_CONSUMPTION, values.MIN_CONSUMPTION)#keep the same amount of city lights on
            self.reservoirPower += self.currentConsumption
            return True
        elif self.subtractFromBattery(self.currentConsumption):
            self.animateCityLights(self.consumptionValues[self.hourCount], values.MAX_CONSUMPTION, values.MIN_CONSUMPTION)
            return True
        else:
            return False

    def animateDistributionLine(self):
        super().animateDistributionLine()
        if not self.switch1Closed:
            self.board.distributionRight.stopPowerFlow()

    def animateSubstation(self):
        self.board.substation.setLED(Substation.LED1_ADDR, self.switch1Closed)
        self.board.substation.setLED(Substation.LED2_ADDR, self.switch2Closed)
        self.board.substation.setLED(Substation.LED3_ADDR, self.switch3Closed)

    def iterateLoop(self):
        super().iterateLoop()
        self.animateSubstation()

    def setSW1Closed(self, closed):
        self.switch1Closed = closed

    def setSW2Closed(self, closed):
        self.switch2Closed = closed

    def setSW3Closed(self, closed):
        self.switch3Closed = closed

    def getUIData(self):
        return [self.solarGenerationValues[self.hourCount], 
        self.windPower,
        self.reservoirPower,
        self.currentConsumption, 
        self.totalRenewableSupply,
        self.batteryRemaining,
        self.reservoirLevel,
        self.dayCount,
        self.hourCount,
        self.switch1Closed,
        self.switch2Closed,
        self.switch3Closed]