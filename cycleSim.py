import time
import matplotlib.pyplot as plt
from plotting import GraphsProcessManager
import random
import values
import threading


class CycleSimThread(threading.Thread):
    
    def __init__(self, board, mainWindow, graphManager):
        self.graphManager = graphManager
        self.board = board
        self.cycleModeObj = CycleSim(board, self.graphManager)
        self.stopEvent = threading.Event()
        self.mainWindow = mainWindow
        board.resetBoard()
        threading.Thread.__init__(self)
        

    def run(self):
        self.stopEvent.clear()
        self.graphManager.showPlots()
        while (not self.stopEvent.is_set()) and (self.cycleModeObj.getStillRunning()):
            self.cycleModeObj.iterateLoop()

        if (not self.stopEvent.is_set()) and (not self.cycleModeObj.getStillRunning()):
            self.cleanUp()

    def cleanUp(self):
        self.graphManager.hidePlots()
        self.board.resetBoard()
        self.mainWindow.setTaskRunning(False)

    def join(self, timeOut = None):
        self.stopEvent.set()  
        self.cleanUp()     
        threading.Thread.join(self,timeOut)

    def configure(self, typeOfDay, daylightHours, windPresent, numLoops, randomiseWind = False, windmillSwitchingPeriod = 1, windAmplitude = 0):
        self.cycleModeObj.configure(typeOfDay, daylightHours, windPresent, numLoops, randomiseWind, windmillSwitchingPeriod, windAmplitude)

    


class CycleSim():
    #City is powered by reservoir
    #Solar and wind sources charge battery
    #battery pumps water to reservoir reservoir during night

    def __init__(self, board, graphManager):
        self.board = board
        self.graphManager = graphManager

        self.batteryRemaining = 50 #percentage
        self.reservoirLevel = 50 #percentage

        self.windStateCount = 0
        self.dayCount = 0
        self.hourCount = 0
        self.stillRunning = True     

    def iterateLoop(self):

        if self.dayCount == self.numLoops or not self.stillRunning:
            self.stillRunning = False
            return

        if self.hourCount == 23:
            self.hourCount = 0
            self.dayCount += 1

            if self.dayCount == self.numLoops:
                self.stillRunning = False
                return

            print("New day")
        else:
            self.hourCount += 1
                      
                        
        self.reservoirPower = 0

        self.addToBattery(self.solarGenerationValues[self.hourCount])

        if self.randomiseWind:
            self.windPowerGenerationUnits = self.getRandomWindPower()
            self.addToBattery(self.windPowerGenerationUnits)
        else:
            if self.board.windmills.areWindmillsOn():                    
                self.addToBattery(self.windPowerGenerationUnits)

        #only animate the city lights if we have enough capacity in the reservoir or battery
        if self.subtractFromReservoir(self.consumptionValues[self.hourCount]):
            self.animateCityLights(self.consumptionValues[self.hourCount], values.MAX_CONSUMPTION, values.MIN_CONSUMPTION)
            self.reservoirPower += self.consumptionValues[self.hourCount]
        elif self.subtractFromBattery(self.consumptionValues[self.hourCount]):
            self.animateCityLights(self.consumptionValues[self.hourCount], values.MAX_CONSUMPTION, values.MIN_CONSUMPTION)
        else:
            self.board.lightCityBlocks(0)      
            print("Energy depleted!")
            self.stillRunning = False
            return
                            
        #when we have minimum consumption use battery to pump reservoir
        #can assume battery is discharing because reservoir recharge rate is higher than sum of solar and wind generation
        if self.consumptionValues[self.hourCount] == values.MIN_CONSUMPTION:

            #only transfer energy to reservoir if we have enough in the battery
            if self.subtractFromBattery(values.RESERVOIR_RECHARGE_RATE):
                    self.addToReservoir(values.RESERVOIR_RECHARGE_RATE)
                    self.reservoirPower -= values.RESERVOIR_RECHARGE_RATE
       

        #plotting
        windPower = 0
        totalRenewableSupply = self.solarGenerationValues[self.hourCount] + self.reservoirPower

        if self.board.windmills.areWindmillsOn():
            windPower += self.windPowerGenerationUnits
            totalRenewableSupply += self.windPowerGenerationUnits

        self.graphManager.setRenewablePowers(self.solarGenerationValues[self.hourCount], windPower, self.reservoirPower)
        self.graphManager.setSupplyDemand(totalRenewableSupply, self.consumptionValues[self.hourCount])
        self.graphManager.setStoredEnergy(self.batteryRemaining, self.reservoirLevel)

        #storage animation
        self.board.lightReservoir(self.reservoirLevel)
        self.animateBattery()

        if self.randomiseWind:
            if self.windPowerGenerationUnits != 0:
                self.board.windmills.startWindmills()
            else:
                self.board.windmills.stopWindmills()
        else:
            if self.windPresent:
                self.animateWindmillsRegular()

        print("Hour", str(self.hourCount))
        print("City consumption: ", str(self.consumptionValues[self.hourCount]))
        print("Solar Panel Generation: ", str(self.solarGenerationValues[self.hourCount]))
        print("Wind Generation: ", str(self.windPowerGenerationUnits))
        print("Battery Level: ", str(self.batteryRemaining))
        print("Reservoir Level: ", str(self.reservoirLevel))
        # print("Battery Charging: ", str(self.batteryCharging))

        time.sleep(1.5)

    def getStillRunning(self):
        return self.stillRunning

    def calculateWindPower(self, amplitude):
        return round(values.MAX_WIND_POWER_GENERATION * amplitude / 10,  2)

    def getRandomWindPower(self):
        randomAmplitude = random.randint(0, 10)
        randomPower = self.calculateWindPower(randomAmplitude)       

        return randomPower

    def animateCityLights(self, consumption, maxConsumption, minConsumption):
        maxConsumptionDelta = maxConsumption - minConsumption

        consumptionAboveMin = consumption - minConsumption

        cityLightsCoefficent = consumptionAboveMin/maxConsumptionDelta
        self.board.lightCityBlocks(cityLightsCoefficent)     


    def setupSolarGenerationValues(self, typeOfDay, daylightHours):
        sunrise = 12 - int(daylightHours/2)
        sunset = 12 + int(daylightHours/2)

        if typeOfDay == "Sunny":
            solarGeneration = values.SUNNY_DAY_SOLAR_GENERATION
        else:
            solarGeneration = values.CLOUDY_DAY_SOLAR_GENERATION

        self.solarGenerationValues = []

        for i in range(0, sunrise):
            self.solarGenerationValues.append(0)

        for i in range(sunrise, sunset):
            self.solarGenerationValues.append(solarGeneration)

        for i in range(sunset, 24):
            self.solarGenerationValues.append(0)
    
    
    def setupConsumptionValues(self, maxConsumption, minConsumption, wakeupTime, sleepTime):
        self.consumptionValues = []
        
        
        for i in range(0, wakeupTime):
            self.consumptionValues.append(minConsumption)
        

        consumptionDelta = maxConsumption - minConsumption

        consumption = 0
        for i in range(1, 13 - wakeupTime):
            consumption = minConsumption + (consumptionDelta * i/(13-wakeupTime))
            consumption = round(consumption, 2)
            self.consumptionValues.append(consumption)

        for i in range(12 , sleepTime):
            self.consumptionValues.append(maxConsumption)

        for i in range(sleepTime, 24):
            consumption = maxConsumption - (consumptionDelta * (i - sleepTime + 1)/(24-sleepTime))
            consumption = round(consumption)
            self.consumptionValues.append(consumption)

    def animateWindmillsRegular(self):
        if self.windStateCount == self.windmillSwitchingPeriod:
            currentWindState = self.board.windmills.areWindmillsOn()
            self.windStateCount = 1
            if currentWindState:
                self.board.windmills.stopWindmills()
            else:
                self.board.windmills.startWindmills()
        else:
            self.windStateCount += 1

    def configure(self, typeOfDay, daylightHours, windPresent, numLoops, randomiseWind, windmillSwitchingPeriod, windAmplitude):
        self.typeOfDay = typeOfDay
        self.daylightHours = daylightHours
        self.windPresent = windPresent
        self.randomiseWind = randomiseWind
        self.windmillSwitchingPeriod = windmillSwitchingPeriod
        self.windAmplitude = windAmplitude
        self.numLoops = numLoops

        self.setupConsumptionValues(values.MAX_CONSUMPTION, values.MIN_CONSUMPTION, values.SIM_WAKEUP_TIME, values.SIM_SLEEP_TIME)
        self.setupSolarGenerationValues(self.typeOfDay, self.daylightHours)

        if windPresent:
            if not randomiseWind:             
                self.windPowerGenerationUnits = self.calculateWindPower(windAmplitude)
        else:
            self.windPowerGenerationUnits = 0


        if typeOfDay == "Sunny":
            maxPower = max(values.MAX_WIND_POWER_GENERATION, values.SUNNY_DAY_SOLAR_GENERATION, values.MAX_CONSUMPTION)
            maxPowerSum = values.MAX_WIND_POWER_GENERATION + values.SUNNY_DAY_SOLAR_GENERATION + values.MAX_CONSUMPTION
            
        else:
            maxPower = max(values.MAX_WIND_POWER_GENERATION, values.CLOUDY_DAY_SOLAR_GENERATION, values.MAX_CONSUMPTION)
            maxPowerSum = values.MAX_WIND_POWER_GENERATION + values.CLOUDY_DAY_SOLAR_GENERATION + values.MAX_CONSUMPTION

        # self.graphManager.configure(maxPower, -values.RESERVOIR_RECHARGE_RATE, maxPowerSum, -values.MAX_CONSUMPTION - values.RESERVOIR_RECHARGE_RATE)

    def animateBattery(self):
        #changes colour when windmills are being driven        
        self.board.fuelCell.setEnergyLevels(self.batteryRemaining, True, self.board.windmills.areWindmillsOn())
          
    
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
    
