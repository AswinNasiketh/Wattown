import time
from plotting import *
import matplotlib.pyplot as plt
import random
import values

class GameMode():
    def __init__(self, gameWindow, mainWindow, board):
        self.board = board
        self.gameWindow = gameWindow
        gameWindow.setGameModeObj(self)

        self.mainWindow = mainWindow

        self.powerPlotter = PowerGraph()
        self.supplyDemandPlotter = ConsumptionSupplyGraph()
        self.storagePlotter = StoredEnergyGraph()        

        #states
        self.RESERVOIR_NO_ACTIVITY = 0
        self.RESERVOIR_GATE_OPENING = 1
        self.RESERVOIR_GATE_OPEN = 2
        self.RESRVOIR_GATE_CLOSING = 3
        self.RESERVOIR_PUMP_TURNING_ON = 4
        self.RESERVOIR_PUMP_ON = 5
        self.RESERVOIR_PUMP_TURNING_OFF = 6

        self.RESERVOIR_MAX_OUTPUT_POWER = 4
        self.RESERVOIR_MAX_INPUT_POWER = -2


    def mainLoop(self):
        self.currentHour = 0
        self.currentDay = 1
        self.windStateCount = 0
        self.reservoirPower = 0
        reservoirEnergy = 100
        previousBatteryEnergy = 20
        batteryEnergy = 20
        wastedEnergy = 0
        demandNotMet = 0

        self.reservoirState = self.RESERVOIR_NO_ACTIVITY

        fig = plt.figure(figsize=(8, 9), dpi=80)
        plt.subplots_adjust(hspace=0.4)
        self.powerPlotter.setupFigure(fig)
        self.supplyDemandPlotter.setupFigure(fig)
        self.storagePlotter.setupFigure(fig)

        plt.ion()
        plt.show()

        self.gameModeRunning = True
        gameNotLost = True     
        while self.gameModeRunning and gameNotLost:
            renewableSurplus = 0
            renewableSurplus -= self.consumptionValues[self.currentHour]
            renewableSurplus += self.solarGenerationValues[self.currentHour]
            renewableSurplus += self.reservoirPower

            if self.randomiseWind:
                self.windmillDrivingFrequency, self.windPower = self.getRandomWindParams()
                renewableSurplus += self.windPower
            else:
                if self.board.areWindmillsOn():
                    renewableSurplus += self.windPower

            reservoirEnergy -= self.reservoirPower

            previousBatteryEnergy = batteryEnergy
            batteryEnergy += renewableSurplus

            if batteryEnergy > 100:
                wastedEnergy += batteryEnergy - 100
                batteryEnergy = 100
            elif batteryEnergy < 0:
                demandNotMet -= batteryEnergy
                batteryEnergy = 0

            if reservoirEnergy <= 0:
                if self.reservoirState == self.RESERVOIR_GATE_OPEN:
                    self.reservoirState = self.RESERVOIR_NO_ACTIVITY
                self.reservoirPower = 0
                reservoirEnergy = 0
                self.gameWindow.disableDrainStartButton()
            else:
                if self.reservoirState == self.RESERVOIR_NO_ACTIVITY:
                    self.gameWindow.enableDrainStartButton()

            if wastedEnergy > 5:
                gameNotLost = False
                self.stopGameMode()
            
            if demandNotMet > 5:
                gameNotLost = False
                self.stopGameMode()               
        
            self.incrementTime()

            self.supplyDemandPlotter.setConsumption(self.consumptionValues[self.currentHour])
            self.storagePlotter.setRemainingEnergies(batteryEnergy,reservoirEnergy)

            if self.board.areWindmillsOn():
                self.powerPlotter.setPowers(self.solarGenerationValues[self.currentHour], self.windPower, self.reservoirPower)
                self.supplyDemandPlotter.setRenewableSupply(self.solarGenerationValues[self.currentHour] + self.windPower + self.reservoirPower)
            else:
                self.powerPlotter.setPowers(self.solarGenerationValues[self.currentHour], 0, self.reservoirPower)
                self.supplyDemandPlotter.setRenewableSupply(self.solarGenerationValues[self.currentHour] + self.reservoirPower)

            self.powerPlotter.animate()
            self.supplyDemandPlotter.animate()
            self.storagePlotter.animate()

            plt.pause(0.001)

            self.gameWindow.updateDisplayedTime(self.currentDay, self.currentHour)
            self.gameWindow.updateReservoirStateDisplay(self.reservoirState)
            self.gameWindow.updateWastedDemandNotMetDisplay(wastedEnergy, demandNotMet)
            

            if self.randomiseWind:
                if self.windPower != 0:
                    self.board.driveWindmills(self.windmillDrivingFrequency)
                else:
                    self.board.stopWindmills()
            else:
                self.driveWindmillsRegular()

            self.animateBattery(batteryEnergy, previousBatteryEnergy)
            self.animateCityLights(self.consumptionValues[self.currentHour], values.MAX_CONSUMPTION, values.MIN_CONSUMPTION)
            self.animateReservoir(reservoirEnergy)

            time.sleep(1.5)

        if not gameNotLost:
            self.gameWindow.gameLost()
        
        plt.close(fig)
        self.board.resetBoard()
    
    def getRandomWindParams(self):
        randomAmplitude = random.randint(0, 10)
        randomPower = self.calculateWindPower(randomAmplitude)       

        return randomAmplitude + 6, randomPower

    def configure(self, typeOfDay, daylightHours, randomiseWind, windmillSwitchingPeriod = None, windAmplitdue = None):
        self.typeOfDay = typeOfDay
        self.daylightHours = daylightHours
        self.setupSolarGenerationValues(typeOfDay, daylightHours)
        self.setupConsumptionValues(values.MAX_CONSUMPTION, values.MIN_CONSUMPTION, values.SIM_WAKEUP_TIME, values.SIM_SLEEP_TIME)
        self.randomiseWind = randomiseWind

        if not randomiseWind:
            self.windmillSwitchingPeriod = windmillSwitchingPeriod
            self.windmillDrivingFrequency = windAmplitdue + 6        
            self.windPower = self.calculateWindPower(windAmplitdue)

        if typeOfDay == "Sunny":
            maxPower = max(values.MAX_WIND_POWER_GENERATION, values.SUNNY_DAY_SOLAR_GENERATION, self.RESERVOIR_MAX_OUTPUT_POWER)
            maxPowerSum = values.MAX_WIND_POWER_GENERATION + values.SUNNY_DAY_SOLAR_GENERATION + self.RESERVOIR_MAX_OUTPUT_POWER
            
        else:
            maxPower = max(values.MAX_WIND_POWER_GENERATION, values.CLOUDY_DAY_SOLAR_GENERATION, self.RESERVOIR_MAX_OUTPUT_POWER)
            maxPowerSum = values.MAX_WIND_POWER_GENERATION + values.CLOUDY_DAY_SOLAR_GENERATION + self.RESERVOIR_MAX_OUTPUT_POWER

        self.powerPlotter.configure(maxPower, self.RESERVOIR_MAX_INPUT_POWER)
        self.supplyDemandPlotter.configure(maxPowerSum, -values.MAX_CONSUMPTION + self.RESERVOIR_MAX_INPUT_POWER)
        

    def calculateWindPower(self, amplitude):
        return round(values.MAX_WIND_POWER_GENERATION * amplitude / 10,  2)

    def incrementTime(self):
        self.currentHour += 1
        if self.currentHour > 23:
            self.currentHour = 0
            self.currentDay += 1

    def driveWindmillsRegular(self):
        if self.windStateCount == self.windmillSwitchingPeriod:
            currentWindState = self.board.areWindmillsOn()
            self.windStateCount = 1
            if currentWindState:
                self.board.stopWindmills()
            else:
                self.board.driveWindmills(self.windmillDrivingFrequency)
        else:
            self.windStateCount += 1

    def animateCityLights(self, consumption, maxConsumption, minConsumption):
        maxConsumptionDelta = maxConsumption - minConsumption

        consumptionAboveMin = consumption - minConsumption

        cityLightsCoefficient = consumptionAboveMin/maxConsumptionDelta

        self.board.lightCityBlocks(cityLightsCoefficient)
                
    def animateBattery(self, currentBatteryLevel, previousBatteryLevel):
        batteryLevelChange = currentBatteryLevel - previousBatteryLevel

        #charging
        if batteryLevelChange > 0:
            batteryLEDcolour = (int(values.LED_BLUE_MAX[0] * (currentBatteryLevel/100)),
            int(values.LED_BLUE_MAX[1] * (currentBatteryLevel/100)),
            int(values.LED_BLUE_MAX[2] * (currentBatteryLevel/100)))

            self.board.setFuelCellLEDs(batteryLEDcolour)
            self.board.pulseFuelCell()
        elif batteryLevelChange < 0:
            #discharging
            batteryLEDcolour = (int(values.LED_YELLOW_MAX[0] * (currentBatteryLevel/100)),
            int((values.LED_YELLOW_MAX[1] * (currentBatteryLevel/100))),
            int((values.LED_YELLOW_MAX[2] * (currentBatteryLevel/100))))

            self.board.setFuelCellLEDs(batteryLEDcolour)
            self.board.pulseFuelCell()
        elif  batteryLevelChange == 0:
            if currentBatteryLevel == 0:
                self.board.setFuelCellLEDs(values.LED_RED_DIM)
            elif currentBatteryLevel == 100:
                self.board.setFuelCellLEDs(values.LED_GREEN_BRIGHT)

    def animateReservoir(self, reservoirLevel):
        if reservoirLevel == 0:
            level0Colour = (0,0,0)
            level1Colour = (0,0,0)
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif reservoirLevel > 0 and reservoirLevel < 25:
            level0Colour = values.LED_WATER_BLUE
            level1Colour = (0,0,0)
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif reservoirLevel >= 25 and reservoirLevel < 50:
            level0Colour = values.LED_WATER_BLUE
            level1Colour = values.LED_WATER_BLUE
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif reservoirLevel >= 50 and reservoirLevel < 75:
            level0Colour = values.LED_WATER_BLUE
            level1Colour = values.LED_WATER_BLUE
            level2Colour = values.LED_WATER_BLUE
            level3Colour = (0,0,0)
        elif reservoirLevel >= 75:
            level0Colour = values.LED_WATER_BLUE
            level1Colour = values.LED_WATER_BLUE
            level2Colour = values.LED_WATER_BLUE
            level3Colour = values.LED_WATER_BLUE

        self.board.setReservoirLEDs(level0Colour,level1Colour,level2Colour,level3Colour)

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

    def setReservoirPower(self, reservoirPower):
        self.reservoirPower = reservoirPower

    def setReservoirState(self, reservoirState):
        self.reservoirState = reservoirState

    def getReservoirPower(self):
        return self.reservoirPower

    def stopGameMode(self):
        self.gameModeRunning = False
        self.board.resetBoard()
        self.mainWindow.setTaskRunning(False)