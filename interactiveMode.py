import time

class InteractiveMode():

    def __init__(self, window, board):
        self.window = window
        self.board = board

        self.PV_THRESHOLD = 1.5
        self.WINDMILL_THRESHOLD = 2.0

        self.PV_GENERATION_UNIT = 5
        self.WINDMILL_GENERATION_UNIT = 2
        self.CONSUMPTION = 3

        self.currentBatteryLevel = 0
        self.previousBatteryLevel = 0

        self.LED_RED_DIM = (100, 0 , 0)
        self.LED_YELLOW_MAX = (242, 194, 99)
        self.LED_BLUE_MAX = (94, 193, 255)
        self.LED_GREEN_BRIGHT = (97, 255, 94)
        self.LED_WATER_BLUE = (94,155,255)

    def interactiveModeLoop(self):
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

            time.sleep(1)
        
        self.board.resetBoard()
        
    
    def areSolarPanelsOn(self):
        solarPanelVoltage = self.board.getSolarPanelVoltage()

        if solarPanelVoltage >= self.PV_THRESHOLD:
            return True
        else:
            return False

    def getWindmillsBlown(self):
        windmillsBlown = 0
        windmillVoltages = self.board.getWindmillVoltages()

        for i in range(len(windmillVoltages)):
            if windmillVoltages[i] >= self.WINDMILL_THRESHOLD:
                windmillsBlown += 1

        return windmillsBlown

    def animateBattery(self):
        batteryLevelChange = self.currentBatteryLevel - self.previousBatteryLevel

        #charging
        if batteryLevelChange > 0:
            batteryLEDcolour = (self.LED_BLUE_MAX[0] * (self.currentBatteryLevel/100),
            self.LED_BLUE_MAX[1] * (self.currentBatteryLevel/100),
            self.LED_BLUE_MAX[2] * (self.currentBatteryLevel/100))

            self.board.setFuelCellLEDs(batteryLEDcolour)
            self.board.turnOnFuelCell()
        elif batteryLevelChange < 0:
            #discharging
            batteryLEDcolour = (self.LED_YELLOW_MAX[0] * (self.currentBatteryLevel/100),
            self.LED_YELLOW_MAX[1] * (self.currentBatteryLevel/100),
            self.LED_YELLOW_MAX[2] * (self.currentBatteryLevel/100))

            self.board.setFuelCellLEDs(batteryLEDcolour)
            self.board.turnOffFuelCell()
        elif  batteryLevelChange == 0:
            self.board.turnOffFuelCell()

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



    