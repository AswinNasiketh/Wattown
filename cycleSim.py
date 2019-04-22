import time
import threading
import matplotlib.pyplot as plt
from plotting import *
import random

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

        #1GW = 0.1 units
        self.SUNNY_DAY_SOLAR_GENERATION = 1.28 #UK solar power capacity = 12.8GW
        self.CLOUDY_DAY_SOLAR_GENERATION = 0.64 #half max capacity for cloudy day

        self.MAX_WIND_POWER_GENERATION = 2 #UK wind power capacity = 20.7GW

        self.MAX_CONSUMPTION = 3.4 #UK max power demand on 06/04/19 was 34GW
        self.MIN_CONSUMPTION = 2.46 #UK min power demand on 06/04/19 was 24.6GW http://gridwatch.co.uk/

        self.SIM_WAKEUP_TIME = 6 #6AM
        self.SIM_SLEEP_TIME = 20 #8PM

        self.RESERVOIR_RECHARGE_RATE = 5

        self.LED_CITY_LIGHTS_YELLOW_MAX = (244, 217, 66)
        self.LED_CITY_LIGHTS_YELLOW_MIN = (122, 108, 33)
        self.LED_WATER_BLUE = (94,155,255)

        self.LED_RED_DIM = (100, 0 , 0)
        self.LED_YELLOW_MAX = (242, 194, 99)
        self.LED_BLUE_MAX = (94, 193, 255)
        self.LED_GREEN_BRIGHT = (97, 255, 94)

        self.city_lights_yellow_delta = (self.LED_CITY_LIGHTS_YELLOW_MAX[0] - self.LED_CITY_LIGHTS_YELLOW_MIN[0],
        self.LED_CITY_LIGHTS_YELLOW_MAX[1] - self.LED_CITY_LIGHTS_YELLOW_MIN[1],
        self.LED_CITY_LIGHTS_YELLOW_MAX[2] - self.LED_CITY_LIGHTS_YELLOW_MIN[2])

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

        self.batteryCharging = False

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
                    self.windmillDrivingFrequency, self.windPowerGenerationUnits = self.getRandomWindParams()
                    self.addToBattery(self.windPowerGenerationUnits)
                else:
                    if self.board.areWindmillsOn():                    
                        self.addToBattery(self.windPowerGenerationUnits)

                #only animate the city lights if we have enough capacity in the reservoir or battery
                if self.subtractFromReservoir(self.consumptionValues[i]):
                    self.animateCityLights(self.consumptionValues[i], self.MAX_CONSUMPTION, self.MIN_CONSUMPTION)
                    self.reservoirPower += self.consumptionValues[i]
                elif self.subtractFromBattery(self.consumptionValues[i]):
                    self.animateCityLights(self.consumptionValues[i], self.MAX_CONSUMPTION, self.MIN_CONSUMPTION)
                else:
                    self.board.setCityLEDs((0,0,0))      
                    print("Energy depleted!")
                    self.runOuterLoop = False
                    break
                                    
                #when we have minimum consumption use battery to pump reservoir
                #can assume battery is discharing because reservoir recharge rate is higher than sum of solar and wind generation
                if self.consumptionValues[i] == self.MIN_CONSUMPTION:
                    self.batteryCharging = False

                    #only transfer energy to reservoir if we have enough in the battery
                    if self.subtractFromBattery(self.RESERVOIR_RECHARGE_RATE):
                         self.addToReservoir(self.RESERVOIR_RECHARGE_RATE)
                         self.reservoirPower -= self.RESERVOIR_RECHARGE_RATE

                #otherwise only charge battery   
                else:
                    self.batteryCharging = True       

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
                self.animateReservoir(self.reservoirLevel)
                self.animateBattery()

                if self.randomiseWind:
                    if self.windPowerGenerationUnits != 0:
                        self.board.driveWindmills(self.windmillDrivingFrequency)
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
                print("Battery Charging: ", str(self.batteryCharging))

                time.sleep(2.5)

        #clean up before end
        plt.close(fig)
        self.board.resetBoard()
        self.mainWindow.setTaskRunning(False)

    def calculateWindPower(self, amplitude):
        return round(self.MAX_WIND_POWER_GENERATION * amplitude / 10,  2)

    def getRandomWindParams(self):
        randomAmplitude = random.randint(0, 10)
        randomPower = self.calculateWindPower(randomAmplitude)       

        return randomAmplitude + 6, randomPower

    def animateCityLights(self, consumption, maxConsumption, minConsumption):
        maxConsumptionDelta = maxConsumption - minConsumption

        consumptionAboveMin = consumption - minConsumption

        cityLightsCoefficent = consumptionAboveMin/maxConsumptionDelta
    

        cityLightsColour = (int(self.city_lights_yellow_delta[0] * cityLightsCoefficent) + self.LED_CITY_LIGHTS_YELLOW_MIN[0],
        int(self.city_lights_yellow_delta[1] * cityLightsCoefficent) + self.LED_CITY_LIGHTS_YELLOW_MIN[1],
        int(self.city_lights_yellow_delta[2] * cityLightsCoefficent) + self.LED_CITY_LIGHTS_YELLOW_MIN[2])

        self.board.setCityLEDs(cityLightsColour)    


    def setupSolarGenerationValues(self, typeOfDay, daylightHours):
        sunrise = 12 - int(daylightHours/2)
        sunset = 12 + int(daylightHours/2)

        if typeOfDay == "Sunny":
            solarGeneration = self.SUNNY_DAY_SOLAR_GENERATION
        else:
            solarGeneration = self.CLOUDY_DAY_SOLAR_GENERATION

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
                self.board.driveWindmills(self.windmillDrivingFrequency)
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

        self.setupConsumptionValues(self.MAX_CONSUMPTION, self.MIN_CONSUMPTION, self.SIM_WAKEUP_TIME, self.SIM_SLEEP_TIME)
        self.setupSolarGenerationValues(self.typeOfDay, self.daylightHours)

        if windPresent:
            if not randomiseWind:             
                self.windPowerGenerationUnits = self.calculateWindPower(windAmplitude)
                self.windmillDrivingFrequency = self.windAmplitude + 6
                print("Windmill Driving Frequency: ", str(self.windmillDrivingFrequency))
        else:
            self.windPowerGenerationUnits = 0


        if typeOfDay == "Sunny":
            maxPower = max(self.MAX_WIND_POWER_GENERATION, self.SUNNY_DAY_SOLAR_GENERATION, self.MAX_CONSUMPTION)
            maxPowerSum = self.MAX_WIND_POWER_GENERATION + self.SUNNY_DAY_SOLAR_GENERATION + self.MAX_CONSUMPTION
            
        else:
            maxPower = max(self.MAX_WIND_POWER_GENERATION, self.CLOUDY_DAY_SOLAR_GENERATION, self.MAX_CONSUMPTION)
            maxPowerSum = self.MAX_WIND_POWER_GENERATION + self.CLOUDY_DAY_SOLAR_GENERATION + self.MAX_CONSUMPTION

        self.powerPlotter.configure(maxPower, self.RESERVOIR_RECHARGE_RATE)
        self.supplyDemandPlotter.configure(maxPowerSum, -self.MAX_CONSUMPTION - self.RESERVOIR_RECHARGE_RATE)

    def animateReservoir(self, reservoirLevel):
        if reservoirLevel == 0:
            level0Colour = (0,0,0)
            level1Colour = (0,0,0)
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif reservoirLevel > 0 and reservoirLevel < 25:
            level0Colour = self.LED_WATER_BLUE
            level1Colour = (0,0,0)
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif reservoirLevel >= 25 and reservoirLevel < 50:
            level0Colour = self.LED_WATER_BLUE
            level1Colour = self.LED_WATER_BLUE
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif reservoirLevel >= 50 and reservoirLevel < 75:
            level0Colour = self.LED_WATER_BLUE
            level1Colour = self.LED_WATER_BLUE
            level2Colour = self.LED_WATER_BLUE
            level3Colour = (0,0,0)
        elif reservoirLevel >= 75:
            level0Colour = self.LED_WATER_BLUE
            level1Colour = self.LED_WATER_BLUE
            level2Colour = self.LED_WATER_BLUE
            level3Colour = self.LED_WATER_BLUE

        self.board.setReservoirLEDs(level0Colour,level1Colour,level2Colour,level3Colour)

    def animateBattery(self):
        #charging
        if self.batteryCharging:
            batteryLEDcolour = (int(self.LED_BLUE_MAX[0] * (self.batteryRemaining/100)),
            int(self.LED_BLUE_MAX[1] * (self.batteryRemaining/100)),
            int(self.LED_BLUE_MAX[2] * (self.batteryRemaining/100)))
        else:
            #discharging
            batteryLEDcolour = (int(self.LED_YELLOW_MAX[0] * (self.batteryRemaining/100)),
            int((self.LED_YELLOW_MAX[1] * (self.batteryRemaining/100))),
            int((self.LED_YELLOW_MAX[2] * (self.batteryRemaining/100))))

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
    
