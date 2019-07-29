from values import *

class Reservoir():

    LEVEL_0_LOWER = 0
    LEVEL_0_UPPER = 2
    LEVEL_1_LOWER = 3
    LEVEL_1_UPPER = 5
    LEVEL_2_LOWER = 6
    LEVEL_2_UPPER = 8
    LEVEL_3_LOWER = 9
    LEVEL_3_UPPER = 11

    def __init__(self, LEDHandle):
        self.LEDHandle = LEDHandle

    #waterLevel can take values from 0 to 4
    def setWaterLevel(self, waterLevel):
        if waterLevel == 0:
            for i in range(Reservoir.LEVEL_0_LOWER, Reservoir.LEVEL_3_UPPER + 1):
                self.LEDHandle[i] = (0, 0, 0)
        elif waterLevel == 1:
            for i in range(Reservoir.LEVEL_0_LOWER, Reservoir.LEVEL_0_UPPER + 1):
                self.LEDHandle[i] = LED_WATER_BLUE

            for i in range(Reservoir.LEVEL_1_LOWER, Reservoir.LEVEL_3_UPPER + 1):
                self.LEDHandle[i] = (0,0,0)
        elif waterLevel == 2:
            for i in range(Reservoir.LEVEL_0_LOWER, Reservoir.LEVEL_1_UPPER + 1):
                self.LEDHandle[i] = LED_WATER_BLUE

            for i in range(Reservoir.LEVEL_2_LOWER, Reservoir.LEVEL_3_UPPER + 1):
                self.LEDHandle[i] = (0,0,0)
        elif waterLevel == 3:
            for i in range(Reservoir.LEVEL_0_LOWER, Reservoir.LEVEL_2_UPPER + 1):
                self.LEDHandle[i] = LED_WATER_BLUE

            for i in range(Reservoir.LEVEL_3_LOWER, Reservoir.LEVEL_3_UPPER + 1):
                self.LEDHandle[i] = (0,0,0)
        elif waterLevel == 4:
            for i in range(Reservoir.LEVEL_0_LOWER, Reservoir.LEVEL_3_UPPER + 1):
                self.LEDHandle[i] = LED_WATER_BLUE