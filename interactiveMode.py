import time

class InteractiveMode():

    def __init__(self, window, board):
        self.window = window
        self.board = board

        currentSolarPanelVoltage = board.getSolarPanelVoltage()
        self.PV_THRESHOLD = currentSolarPanelVoltage + 0.01
        self.WINDMILL_THRESHOLD = 2.0

        self.PV_GENERATION_UNIT = 5
        self.WINDMILL_GENERATION_UNIT = 2
        self.CONSUMPTION = 3

        self.currentBatteryLevel = 0
        self.previousBatteryLevel = 0

        self.LED_RED_DIM = (100, 0 , 0)
        self.LED_YELLOW_MAX = (130, 130, 66)
        self.LED_BLUE_MAX = (94, 193, 255)
        self.LED_GREEN_BRIGHT = (97, 255, 94)
        self.LED_WATER_BLUE = (94,155,255)
        self.LED_CITY_LIGHTS_YELLOW = (163, 145, 44)

    def interactiveModeLoop(self):
        print("Starting interactive mode loop")
        self.board.stopWindmills()
        self.currentBatteryLevel = 0
        self.previousBatteryLevel = 0

        while self.window.getTaskRunning():
            self.previousBatteryLevel = self.currentBatteryLevel

            if self.currentBatteryLevel < 100:

                if self.areSolarPanelsOn():
                    self.currentBatteryLevel += self.PV_GENERATION_UNIT

                self.currentBatteryLevel += self.WINDMILL_GENERATION_UNIT * self.getWindmillsBlown()

            if self.currentBatteryLevel > 100:
                self.currentBatteryLevel = 100 #validation

            if self.currentBatteryLevel > 0:
                self.currentBatteryLevel -= self.CONSUMPTION

            if self.currentBatteryLevel < 0:
                self.currentBatteryLevel = 0 #validation

            self.animateBattery()
            self.animateReservoir()
            self.animateCityLights()
            print("Battery level: " + str(self.currentBatteryLevel))
            time.sleep(1)
        
        self.board.resetBoard()
        
    
    def areSolarPanelsOn(self):
        solarPanelVoltage = self.board.getSolarPanelVoltage()
        print(solarPanelVoltage)

        if solarPanelVoltage >= self.PV_THRESHOLD:
            print("Solar panels on")
            return True
        else:
            print("Solar panels off")
            return False

    def getWindmillsBlown(self):
        windmillsBlown = 0
        windmillVoltages = self.board.getWindmillVoltages()

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
            batteryLEDcolour = (int(self.LED_BLUE_MAX[0] * (self.currentBatteryLevel/100)),
            int(self.LED_BLUE_MAX[1] * (self.currentBatteryLevel/100)),
            int(self.LED_BLUE_MAX[2] * (self.currentBatteryLevel/100)))

            self.board.setFuelCellLEDs(batteryLEDcolour)
            self.board.pulseFuelCell()
        elif batteryLevelChange < 0:
            #discharging
            batteryLEDcolour = (int(self.LED_YELLOW_MAX[0] * (self.currentBatteryLevel/100)),
            int((self.LED_YELLOW_MAX[1] * (self.currentBatteryLevel/100))),
            int((self.LED_YELLOW_MAX[2] * (self.currentBatteryLevel/100))))

            self.board.setFuelCellLEDs(batteryLEDcolour)
        elif  batteryLevelChange == 0:
            if self.currentBatteryLevel == 0:
                self.board.setFuelCellLEDs(self.LED_RED_DIM)
            elif self.currentBatteryLevel == 100:
                self.board.setFuelCellLEDs(self.LED_GREEN_BRIGHT)
        
    def animateReservoir(self):
        if self.currentBatteryLevel == 0:
            level0Colour = (0,0,0)
            level1Colour = (0,0,0)
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif self.currentBatteryLevel > 0 and self.currentBatteryLevel < 25:
            level0Colour = self.LED_WATER_BLUE
            level1Colour = (0,0,0)
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif self.currentBatteryLevel >= 25 and self.currentBatteryLevel < 50:
            level0Colour = self.LED_WATER_BLUE
            level1Colour = self.LED_WATER_BLUE
            level2Colour = (0,0,0)
            level3Colour = (0,0,0)
        elif self.currentBatteryLevel >= 50 and self.currentBatteryLevel < 75:
            level0Colour = self.LED_WATER_BLUE
            level1Colour = self.LED_WATER_BLUE
            level2Colour = self.LED_WATER_BLUE
            level3Colour = (0,0,0)
        elif self.currentBatteryLevel >= 75:
            level0Colour = self.LED_WATER_BLUE
            level1Colour = self.LED_WATER_BLUE
            level2Colour = self.LED_WATER_BLUE
            level3Colour = self.LED_WATER_BLUE

        self.board.setReservoirLEDs(level0Colour,level1Colour,level2Colour,level3Colour)

    def animateCityLights(self):
        if(self.currentBatteryLevel > 0):
            self.board.setCityLEDs(self.LED_CITY_LIGHTS_YELLOW)
        else:
            self.board.setCityLEDs((0,0,0))



    