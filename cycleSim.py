import random
import values
import threading
from distributionLines import DistributionLine


class CycleSimThread(threading.Thread):
    
    def __init__(self, board):
        self.board = board
        self.cycleModeObj = CycleSim(board)
        self.stopEvent = threading.Event()
        board.resetBoard()
        threading.Thread.__init__(self)
        

    def run(self):
        self.stopEvent.clear()

        self.board.transmissionLine.setAllTowersColour(values.LED_WHITE)#to indicate cycle mode is running
        
        while not self.stopEvent.wait(1.5):
            if not self.cycleModeObj.getStillRunning():
                break
            self.cycleModeObj.iterateLoop()
            #will be reset to off when clean up occurs

        #if the stop event isn't set, but the simulation isn't still running
        if (not self.stopEvent.is_set()) and (not self.cycleModeObj.getStillRunning()):
            self.cleanUp()

    def cleanUp(self):
        self.board.resetBoard()

    def join(self, timeOut = None):
        self.stopEvent.set()  
        self.cleanUp()     
        threading.Thread.join(self,timeOut)

    def configure(self,numLoops, sustainable):
        self.cycleModeObj.configure(numLoops, sustainable)

    


class CycleSim():
    #City is powered by reservoir
    #Solar and wind sources charge battery
    #battery pumps water to reservoir reservoir during night

    SUNRISE = 6 #6AM
    SUNSET = 20 #8PM

    def __init__(self, board):
        self.board = board
        # self.graphManager = graphManager

        self.batteryRemaining = 50 #percentage
        self.reservoirLevel = 50 #percentage
        self.windPower = 0
        self.reservoirPower = 0
        self.totalRenewableSupply = 0

        self.dayCount = 0
        self.hourCount = 0
        self.stillRunning = True     

    def iterateLoop(self):

        # if we've done the number of days to simulate, do nothing
        if self.dayCount == self.numLoops or not self.stillRunning:
            self.stillRunning = False
            return
        
        #next day
        if self.hourCount == 23:
            self.hourCount = 0
            self.dayCount += 1

            if self.dayCount == self.numLoops:
                self.stillRunning = False
                return

        else:
            self.hourCount += 1
                      
        #generation                        
        self.addToBattery(self.solarGenerationValues[self.hourCount])
        self.windPower = 0
        if self.isWindBlowing():
            if self.sustainable:
                self.windPower = values.SUSTAINABLE_WIND_POWER_GENERATION
            else:
                self.windPower = values.CURRENT_WIND_POWER_GENERATION
        self.addToBattery(self.windPower)           

        if not self.consumePower():
            #stop simulation if we have no energy
            self.board.lightCityBlocks(0)      
            print("Energy depleted!")
            self.stillRunning = False
            return

        #when we have minimum consumption use battery to pump reservoir
        if self.consumptionValues[self.hourCount] == values.MIN_CONSUMPTION:

            #only transfer energy to reservoir if we have enough in the battery
            if self.subtractFromBattery(values.RESERVOIR_RECHARGE_RATE):
                    self.addToReservoir(values.RESERVOIR_RECHARGE_RATE)
                    self.reservoirPower -= values.RESERVOIR_RECHARGE_RATE
       

        #for UI
        self.totalRenewableSupply = self.solarGenerationValues[self.hourCount] + self.reservoirPower + self.windPower

        #animation
        self.board.lightReservoir(self.reservoirLevel)
        self.animateBattery()
        self.animateWattownSign()
        self.animateDistributionLine()
   
        if self.windPower != 0:
            self.board.windmills.startWindmills()
        else:
            self.board.windmills.stopWindmills()

        print("Hour", str(self.hourCount))
        print("City consumption: ", str(self.consumptionValues[self.hourCount]))
        print("Solar Panel Generation: ", str(self.solarGenerationValues[self.hourCount]))
        print("Wind Generation: ", str(self.windPower))
        print("Battery Level: ", str(self.batteryRemaining))
        print("Reservoir Level: ", str(self.reservoirLevel))

   #returns true if there is sufficient power, otherwise false
    def consumePower(self):
        #only light up the city if we have enough capacity in the reservoir or battery
        self.reservoirPower = 0
        if self.subtractFromReservoir(self.consumptionValues[self.hourCount]):
            self.animateCityLights(self.consumptionValues[self.hourCount], values.MAX_CONSUMPTION, values.MIN_CONSUMPTION)
            self.reservoirPower += self.consumptionValues[self.hourCount]
            return True
        elif self.subtractFromBattery(self.consumptionValues[self.hourCount]):
            self.animateCityLights(self.consumptionValues[self.hourCount], values.MAX_CONSUMPTION, values.MIN_CONSUMPTION)
            return True
        else:
            return False


    def animateWattownSign(self):
        if self.hourCount > self.SUNSET :
            self.board.wattownSign.turnOn()
        else:
            self.board.wattownSign.turnOff()

    def animateDistributionLine(self):
        self.board.distributionMiddle.startPowerFlow()
        self.board.distributionRight.startPowerFlow() # will be reset to off when cleanup occurs

        if self.consumptionValues[self.hourCount] == values.MIN_CONSUMPTION:
            self.board.distributionMiddle.setFrameRate(DistributionLine.SLOW_ANIMATION_FRAME_RATE)
        else:
            self.board.distributionMiddle.setFrameRate(DistributionLine.FAST_ANIMATION_FRAME_RATE)

    def getUIData(self):
        return [self.solarGenerationValues[self.hourCount], 
        self.windPower,
        self.reservoirPower,
        self.consumptionValues[self.hourCount],
        self.totalRenewableSupply,
        self.batteryRemaining,
        self.reservoirLevel,
        self.dayCount,
        self.hourCount]


    def getStillRunning(self):
        return self.stillRunning

    def isWindBlowing(self):
        return random.randint(0,100) > 50 #50/50 chance of wind being present in a day

    def animateCityLights(self, consumption, maxConsumption, minConsumption):
        maxConsumptionDelta = maxConsumption - minConsumption

        consumptionAboveMin = consumption - minConsumption

        cityLightsCoefficent = consumptionAboveMin/maxConsumptionDelta
        self.board.lightCityBlocks(cityLightsCoefficent)     


    def setupSolarGenerationValues(self, sustainable = True):
        self.solarGenerationValues = []
        if sustainable:
            solarPower = values.SUSTAINABLE_SOLAR_GENERATION
        else:
            solarPower = values.CURRENT_SOLAR_GENERATION

        for i in range(0, self.SUNRISE):
            self.solarGenerationValues.append(0)

        for i in range(self.SUNRISE, self.SUNSET):
            self.solarGenerationValues.append(solarPower)

        for i in range(self.SUNSET, 24):
            self.solarGenerationValues.append(0)
    
    
    def setupConsumptionValues(self, maxConsumption, minConsumption):
        self.consumptionValues = []
                
        for i in range(0, self.SUNRISE):
            self.consumptionValues.append(minConsumption)        

        consumptionDelta = maxConsumption - minConsumption

        consumption = 0
        for i in range(1, 13 - self.SUNRISE):
            consumption = minConsumption + (consumptionDelta * i/(13-self.SUNRISE))
            consumption = round(consumption, 2)
            self.consumptionValues.append(consumption)

        for i in range(12 , self.SUNSET):
            self.consumptionValues.append(maxConsumption)

        for i in range(self.SUNSET, 24):
            consumption = maxConsumption - (consumptionDelta * (i - self.SUNSET + 1)/(24-self.SUNSET))
            consumption = round(consumption)
            self.consumptionValues.append(consumption)
        

    def configure(self, numLoops, sustainable = True):
        self.sustainable = sustainable
        self.numLoops = numLoops

        self.setupConsumptionValues(values.MAX_CONSUMPTION, values.MIN_CONSUMPTION)
        self.setupSolarGenerationValues(sustainable)

    def animateBattery(self):
        #changes colour when windmills are being driven        
        self.board.fuelCell.setEnergyLevel(self.batteryRemaining, True, self.board.windmills.areWindmillsOn())
          
    
    def addToBattery(self, unitsToAdd):
        if (self.batteryRemaining + unitsToAdd) > 100:
            self.batteryRemaining = 100
        else:
            self.batteryRemaining += unitsToAdd
        
    def subtractFromBattery(self, unitsToSubtract):
        if(self.batteryRemaining - unitsToSubtract) < 0:
            return False
        else:
            self.batteryRemaining -= unitsToSubtract
            return True
          

    def addToReservoir(self, unitsToAdd):
        if (self.reservoirLevel + unitsToAdd) > 100:
            self.reservoirLevel = 100
        else:
            self.reservoirLevel += unitsToAdd

    def subtractFromReservoir(self, unitsToSubtract):
        if(self.reservoirLevel - unitsToSubtract) < 0:
            return False
        else:
            self.reservoirLevel -= unitsToSubtract
            return True
    
