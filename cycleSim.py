import time
import threading

class CycleSim():

    def __init__(self, board, mainWindow):
        self.board = board
        self.mainWindow = mainWindow

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
        self.LED_YELLOW = (242, 194, 99)
        self.LED_BLUE = (94, 193, 255)
        self.LED_GREEN_BRIGHT = (97, 255, 94)

        self.city_lights_yellow_delta = (self.LED_CITY_LIGHTS_YELLOW_MAX[0] - self.LED_CITY_LIGHTS_YELLOW_MIN[0],
        self.LED_CITY_LIGHTS_YELLOW_MAX[1] - self.LED_CITY_LIGHTS_YELLOW_MIN[1],
        self.LED_CITY_LIGHTS_YELLOW_MAX[2] - self.LED_CITY_LIGHTS_YELLOW_MIN[2])

    def cycleModeLoop(self):
        print("Starting cycle mode loop")


        self.setupConsumptionValues(self.MAX_CONSUMPTION, self.MIN_CONSUMPTION, self.SIM_WAKEUP_TIME, self.SIM_SLEEP_TIME)
        self.setupSolarGenerationValues(self.typeOfDay, self.daylightHours)

        if self.windPresent:
            windPowerGenerationUnits = round(self.MAX_WIND_POWER_GENERATION * self.windAmplitude/14, 2)

            self.windmillDrivingFrequency = self.windAmplitude + 6
            print("Windmill Driving Frequency: ", str(self.windmillDrivingFrequency))

            # runWindmillsLambda = lambda: self.animateWindmills(self.windmillSwitchingPeriod, windmillDrivingFrequency)
            # windmillDriverThread = threading.Thread(target=runWindmillsLambda)
            # windmillDriverThread.daemon = True
            # windmillDriverThread.start()
        else:
            windPowerGenerationUnits = 0
        

        self.batteryRemaining = 50 #percentage
        self.reservoirLevel = 50 #percentage

        self.batteryCharging = False

        batteryAnimatorThread = threading.Thread(target=self.animateBattery)
        batteryAnimatorThread.daemon = True
        batteryAnimatorThread.start()

        self.windStateCount = 0
        
        for j in range(0, self.numLoops):
            print("New day")            

            for i in range(0, 24):

                if not self.mainWindow.getTaskRunning():
                    break           

                self.addToBattery(self.solarGenerationValues[i])

                if self.board.areWindmillsOn():                    
                    self.addToBattery(windPowerGenerationUnits)

                #only animate the city lights if we have enough capacity in the reservoir
                if self.subtractFromReservoir(self.consumptionValues[i]):
                    self.animateCityLights(self.consumptionValues[i], self.MAX_CONSUMPTION, self.MIN_CONSUMPTION)
                else:
                    self.board.setCityLEDs((0,0,0))      

                                    
                #when we have minimum consumption use battery to pump reservoir
                if self.consumptionValues[i] == self.MIN_CONSUMPTION:
                    self.batteryCharging = False

                    #only transfer energy to reservoir if we have enough in the battery
                    if self.subtractFromBattery(self.RESERVOIR_RECHARGE_RATE):
                         self.addToReservoir(self.RESERVOIR_RECHARGE_RATE)     

                #otherwise only charge battery   
                else:
                    self.batteryCharging = True       
                   
                self.animateReservoir(self.reservoirLevel)
                self.animateWindmills()

                print("Hour", str(i))
                print("City consumption: ", str(self.consumptionValues[i]))
                print("Solar Panel Generation: ", str(self.solarGenerationValues[i]))
                if self.board.areWindmillsOn():
                    print("Wind Generation: ", str(windPowerGenerationUnits))
                else:
                    print("Wind Generation: 0")
                print("Battery Level: ", str(self.batteryRemaining))
                print("Reservoir Level: ", str(self.reservoirLevel))
                print("Battery Charging: ", str(self.batteryCharging))
                time.sleep(2.5)

        self.board.resetBoard()
        self.mainWindow.setTaskRunning(False)


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

    def animateWindmills(self):
        if self.windStateCount == self.windmillSwitchingPeriod:
            currentWindState = self.board.areWindmillsOn()
            self.windStateCount = 1
            if currentWindState:
                self.board.stopWindmills()
            else:
                self.board.driveWindmills(self.windmillDrivingFrequency)
        else:
            self.windStateCount += 1
            

    #not being used anymore
    def animateWindmillsAndFuelCell(self, windmillSwitchingPeriod, windmillDrivingFrequency):       
        windmillsOn = False

        for i in range(0, 60, windmillSwitchingPeriod):
            if not self.mainWindow.getTaskRunning():
                break

            if not windmillsOn:
                self.board.driveWindmills(windmillDrivingFrequency)
                windmillsOn = True
                self.pulseFuelCell()
                time.sleep(windmillSwitchingPeriod - 1)
            else:
                self.board.stopWindmills()
                windmillsOn = False
                time.sleep(windmillSwitchingPeriod)
        self.board.stopWindmills()
        self.board.turnOffFuelCell()
            

    def pulseFuelCell(self):
        self.board.turnOnFuelCell()
        time.sleep(0.5)
        self.board.turnOffFuelCell()

    def configure(self, typeOfDay, daylightHours, windPresent, windmillSwitchingPeriod, windAmplitude, numLoops):
        self.typeOfDay = typeOfDay
        self.daylightHours = daylightHours
        self.windPresent = windPresent
        self.windmillSwitchingPeriod = windmillSwitchingPeriod
        self.windAmplitude = windAmplitude
        self.numLoops = numLoops

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
        for i in range(0,60):
            if self.mainWindow.getTaskRunning():
                break

            if self.batteryCharging:
                chargingColour = self.LED_BLUE
            else:
                #if battery is discharging but no charge left
                if self.batteryRemaining == 0:
                    chargingColour = self.LED_RED_DIM
                else:
                    chargingColour = self.LED_YELLOW
            
            if self.batteryRemaining > 20:
                batteryColour = self.LED_GREEN_BRIGHT
            else:
                batteryColour = self.LED_RED_DIM

            self.board.setFuelCellLEDs(chargingColour)
            time.sleep(0.5)
            self.board.setFuelCellLEDs(batteryColour)
            time.sleep(0.5)

        self.board.setFuelCellLEDs((0,0,0))
    
    def addToBattery(self, unitsToAdd):
        if (self.batteryRemaining + unitsToAdd) > 100:
            self.batteryRemaining = 100
        else:
            self.batteryRemaining += unitsToAdd
            threading.Thread(target=self.pulseFuelCell).start()

    def subtractFromBattery(self, unitsToSubtract):
        if(self.batteryRemaining - unitsToSubtract) < 0:
            return False
        else:
            self.batteryRemaining -= unitsToSubtract
            threading.Thread(target=self.pulseFuelCell).start()
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
    
