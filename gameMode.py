import time
import random

class GameMode():
    def __init__(self, gameWindow, mainWindow, board):
        self.board = board
        self.gameWindow = gameWindow
        gameWindow.setGameModeObj(self)

        self.mainWindow = mainWindow

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

        self.RESERVOIR_NO_ACTIVITY = 0
        self.RESERVOIR_GATE_OPENING = 1
        self.RESERVOIR_GATE_OPEN = 2
        self.RESRVOIR_GATE_CLOSING = 3
        self.RESERVOIR_PUMP_TURNING_ON = 4
        self.RESERVOIR_PUMP_ON = 5
        self.RESERVOIR_PUMP_TURNING_OFF = 6


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
                self.gameWindow.enableDrainStartButton()

            if wastedEnergy > 5:
                gameNotLost = False
                self.stopGameMode()
            
            if demandNotMet > 5:
                gameNotLost = False
                self.stopGameMode()               
        
            self.incrementTime()

            self.gameWindow.updateDisplayedTime(self.currentDay, self.currentHour)
            self.gameWindow.updateReservoirStateDisplay(self.reservoirState)
            self.gameWindow.updateEnergyDisplays(batteryEnergy, reservoirEnergy)

            if self.board.areWindmillsOn():
                self.gameWindow.updatePowerDisplays(self.solarGenerationValues[self.currentHour], self.windPower, self.reservoirPower, self.consumptionValues[self.currentHour])
            else:
                self.gameWindow.updatePowerDisplays(self.solarGenerationValues[self.currentHour], 0, self.reservoirPower, self.consumptionValues[self.currentHour])

            self.gameWindow.updateSurplusShortageDisplays(max(0 , renewableSurplus), min(0, renewableSurplus))
            self.gameWindow.updateWastedDemandNotMetDisplay(wastedEnergy, demandNotMet)
            

            if self.randomiseWind:
                if self.windmillDrivingFrequency != 0:
                    self.board.driveWindmills(self.windmillDrivingFrequency)
                else:
                    self.board.stopWindmills()
            else:
                self.driveWindmillsRegular()

            self.animateBattery(batteryEnergy, previousBatteryEnergy)
            self.animateCityLights(self.consumptionValues[self.currentHour], self.MAX_CONSUMPTION, self.MIN_CONSUMPTION)
            self.animateReservoir(reservoirEnergy)

            time.sleep(2.5)

        if not gameNotLost:
            self.gameWindow.gameLost()
        
        self.board.resetBoard()
    
    def getRandomWindParams(self):
        randomAmplitude = random.randint(0, 10)
        randomPower = self.calculateWindPower(randomAmplitude)

        return randomAmplitude + 6, randomPower

    def configure(self, typeOfDay, daylightHours, randomiseWind, windmillSwitchingPeriod = None, windAmplitdue = None):
        self.typeOfDay = typeOfDay
        self.daylightHours = daylightHours
        self.setupSolarGenerationValues(typeOfDay, daylightHours)
        self.setupConsumptionValues(self.MAX_CONSUMPTION, self.MIN_CONSUMPTION, self.SIM_WAKEUP_TIME, self.SIM_SLEEP_TIME)
        self.randomiseWind = randomiseWind

        if not randomiseWind:
            self.windmillSwitchingPeriod = windmillSwitchingPeriod
            self.windmillDrivingFrequency = windAmplitdue + 6        
            self.windPower = self.calculateWindPower(windAmplitdue)
        

    def calculateWindPower(self, amplitude):
        return round(self.MAX_WIND_POWER_GENERATION * amplitude / 10,  2)

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

        cityLightsCoefficent = consumptionAboveMin/maxConsumptionDelta
    

        cityLightsColour = (int(self.city_lights_yellow_delta[0] * cityLightsCoefficent) + self.LED_CITY_LIGHTS_YELLOW_MIN[0],
        int(self.city_lights_yellow_delta[1] * cityLightsCoefficent) + self.LED_CITY_LIGHTS_YELLOW_MIN[1],
        int(self.city_lights_yellow_delta[2] * cityLightsCoefficent) + self.LED_CITY_LIGHTS_YELLOW_MIN[2])

        self.board.setCityLEDs(cityLightsColour)  
                
    def animateBattery(self, currentBatteryLevel, previousBatteryLevel):
        batteryLevelChange = currentBatteryLevel - previousBatteryLevel

        #charging
        if batteryLevelChange > 0:
            batteryLEDcolour = (int(self.LED_BLUE_MAX[0] * (currentBatteryLevel/100)),
            int(self.LED_BLUE_MAX[1] * (currentBatteryLevel/100)),
            int(self.LED_BLUE_MAX[2] * (currentBatteryLevel/100)))

            self.board.setFuelCellLEDs(batteryLEDcolour)
            self.pulseFuelCell()
        elif batteryLevelChange < 0:
            #discharging
            batteryLEDcolour = (int(self.LED_YELLOW_MAX[0] * (currentBatteryLevel/100)),
            int((self.LED_YELLOW_MAX[1] * (currentBatteryLevel/100))),
            int((self.LED_YELLOW_MAX[2] * (currentBatteryLevel/100))))

            self.board.setFuelCellLEDs(batteryLEDcolour)
            self.pulseFuelCell()
        elif  batteryLevelChange == 0:
            if currentBatteryLevel == 0:
                self.board.setFuelCellLEDs(self.LED_RED_DIM)
            elif currentBatteryLevel == 100:
                self.board.setFuelCellLEDs(self.LED_GREEN_BRIGHT)

    def pulseFuelCell(self):
        self.board.turnOnFuelCell()
        time.sleep(0.5)
        self.board.turnOffFuelCell()  

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