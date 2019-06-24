import time
import matplotlib.pyplot as plt
from plotting import *
import random
import values

class CycleSim():
    #City is powered by reservoir
    #Solar and wind sources charge battery
    #battery pumps water to reservoir reservoir during night

    def __init__(self, board, mainWindow):
        self.board = board
        self.mainWindow = mainWindow

        self.powerPlotter = PowerGraph()
        self.supplyDemandPlotter = ConsumptionSupplyGraph()
        self.storagePlotter = StoredEnergyGraph()   

    def cycleModeLoop(self):       

        fig = plt.figure(figsize=(8, 9), dpi=80)
        plt.subplots_adjust(hspace=0.4)
        self.powerPlotter.setupFigure(fig)
        self.supplyDemandPlotter.setupFigure(fig)
        self.storagePlotter.setupFigure(fig)
        plt.ion()
        plt.show()       
        

        self.batteryRemaining = 50 #percentage
        self.reservoirLevel = 50 #percentage

        # self.batteryCharging = False

        self.windStateCount = 0

        print("Starting cycle mode loop")
        self.runOuterLoop = True
        for j in range(0, self.numLoops):
            print("New day")          

            if not self.runOuterLoop:
                break  

            for i in range(0, 24):
                
                if not self.mainWindow.getTaskRunning():
                    self.runOuterLoop = False 
                    break     
                self.runOuterLoop = True
                self.reservoirPower = 0

                self.addToBattery(self.solarGenerationValues[i])

                if self.randomiseWind:
                    self.windPowerGenerationUnits = self.getRandomWindPower()
                    self.addToBattery(self.windPowerGenerationUnits)
                else:
                    if self.board.areWindmillsOn():                    
                        self.addToBattery(self.windPowerGenerationUnits)

                #only animate the city lights if we have enough capacity in the reservoir or battery
                if self.subtractFromReservoir(self.consumptionValues[i]):
                    self.animateCityLights(self.consumptionValues[i], values.MAX_CONSUMPTION, values.MIN_CONSUMPTION)
                    self.reservoirPower += self.consumptionValues[i]
                elif self.subtractFromBattery(self.consumptionValues[i]):
                    self.animateCityLights(self.consumptionValues[i], values.MAX_CONSUMPTION, values.MIN_CONSUMPTION)
                else:
                    self.board.setCityLEDs((0,0,0))      
                    print("Energy depleted!")
                    self.runOuterLoop = False
                    break
                                    
                #when we have minimum consumption use battery to pump reservoir
                #can assume battery is discharing because reservoir recharge rate is higher than sum of solar and wind generation
                if self.consumptionValues[i] == values.MIN_CONSUMPTION:
                    # self.batteryCharging = False

                    #only transfer energy to reservoir if we have enough in the battery
                    if self.subtractFromBattery(values.RESERVOIR_RECHARGE_RATE):
                         self.addToReservoir(values.RESERVOIR_RECHARGE_RATE)
                         self.reservoirPower -= values.RESERVOIR_RECHARGE_RATE

                #otherwise only charge battery   
                else:
                    # self.batteryCharging = True
                    pass       

                #plotting
                self.supplyDemandPlotter.setConsumption(self.consumptionValues[i])
                self.storagePlotter.setRemainingEnergies(self.batteryRemaining,self.reservoirLevel)

                if self.board.areWindmillsOn():
                    self.powerPlotter.setPowers(self.solarGenerationValues[i], self.windPowerGenerationUnits, self.reservoirPower)
                    self.supplyDemandPlotter.setRenewableSupply(self.solarGenerationValues[i] + self.windPowerGenerationUnits + self.reservoirPower)
                else:
                    self.powerPlotter.setPowers(self.solarGenerationValues[i], 0, self.reservoirPower)
                    self.supplyDemandPlotter.setRenewableSupply(self.solarGenerationValues[i] + self.reservoirPower)

                self.powerPlotter.animate()
                self.supplyDemandPlotter.animate()
                self.storagePlotter.animate()

                plt.pause(0.001)

                #board animation
                self.board.lightReservoir(self.reservoirLevel)
                self.animateBattery()

                if self.randomiseWind:
                    if self.windPowerGenerationUnits != 0:
                        self.board.driveWindmills()
                        self.board.pulseFuelCell()
                    else:
                        self.board.stopWindmills()
                else:
                    if self.windPresent:
                        self.animateWindmillsRegular()

                print("Hour", str(i))
                print("City consumption: ", str(self.consumptionValues[i]))
                print("Solar Panel Generation: ", str(self.solarGenerationValues[i]))
                print("Wind Generation: ", str(self.windPowerGenerationUnits))
                print("Battery Level: ", str(self.batteryRemaining))
                print("Reservoir Level: ", str(self.reservoirLevel))
                # print("Battery Charging: ", str(self.batteryCharging))

                time.sleep(1.5)

        #clean up before end
        plt.close(fig)
        self.board.resetBoard()
        self.mainWindow.setTaskRunning(False)

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
            currentWindState = self.board.areWindmillsOn()
            self.windStateCount = 1
            if currentWindState:
                self.board.stopWindmills()
            else:
                self.board.driveWindmills()
                self.board.pulseFuelCell()
        else:
            self.windStateCount += 1

    def configure(self, typeOfDay, daylightHours, windPresent, numLoops, randomiseWind = False, windmillSwitchingPeriod = 1, windAmplitude = 0):
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

        self.powerPlotter.configure(maxPower, -values.RESERVOIR_RECHARGE_RATE)
        self.supplyDemandPlotter.configure(maxPowerSum, -values.MAX_CONSUMPTION - values.RESERVOIR_RECHARGE_RATE)

    def animateBattery(self):
        #changes colour when windmills are being driven
        if self.board.areWindmillsOn():
            batteryLEDcolour = (int(values.LED_BLUE_MAX[0] * (self.batteryRemaining/100)),
            int(values.LED_BLUE_MAX[1] * (self.batteryRemaining/100)),
            int(values.LED_BLUE_MAX[2] * (self.batteryRemaining/100)))
        else:
            batteryLEDcolour = (int(values.LED_YELLOW_MAX[0] * (self.batteryRemaining/100)),
            int((values.LED_YELLOW_MAX[1] * (self.batteryRemaining/100))),
            int((values.LED_YELLOW_MAX[2] * (self.batteryRemaining/100))))

        self.board.setFuelCellLEDs(batteryLEDcolour)             
    
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
    
