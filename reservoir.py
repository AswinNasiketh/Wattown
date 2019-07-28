from values import *

class Reservoir():

    RESERVOIR_LEVEL_0_LOWER = 0
    RESERVOIR_LEVEL_0_UPPER = 2
    RESERVOIR_LEVEL_1_LOWER = 3
    RESERVOIR_LEVEL_1_UPPER = 5
    RESERVOIR_LEVEL_2_LOWER = 6
    RESERVOIR_LEVEL_2_UPPER = 8
    RESERVOIR_LEVEL_3_LOWER = 9
    RESERVOIR_LEVEL_3_UPPER = 11

    def __init__(self, LEDHandle):
        self.LEDHandle = LEDHandle

    #waterLevel can take values from 0 to 4
    def setWaterLevel(self, waterLevel):
        if waterLevel == 0:
            for i in range(RESERVOIR_LEVEL_0_LOWER, RESERVOIR_LEVEL_3_UPPER + 1):
                self.LEDHandle[i] = (0, 0, 0)
        elif waterLevel == 1:
            for i in range(RESERVOIR_LEVEL_0_LOWER, RESERVOIR_LEVEL_0_UPPER + 1):
                self.LEDHandle[i] = LED_WATER_BLUE

            for i in range(RESERVOIR_LEVEL_1_LOWER, RESERVOIR_LEVEL_3_UPPER + 1):
                self.LEDHandle[i] = (0,0,0)
        elif waterLevel == 2:
            for i in range(RESERVOIR_LEVEL_0_LOWER, RESERVOIR_LEVEL_1_UPPER + 1):
                self.LEDHandle[i] = LED_WATER_BLUE

            for i in range(RESERVOIR_LEVEL_2_LOWER, RESERVOIR_LEVEL_3_UPPER + 1):
                self.LEDHandle[i] = (0,0,0)
        elif waterLevel == 3:
            for i in range(RESERVOIR_LEVEL_0_LOWER, RESERVOIR_LEVEL_2_UPPER + 1):
                self.LEDHandle[i] = LED_WATER_BLUE

            for i in range(RESERVOIR_LEVEL_3_LOWER, RESERVOIR_LEVEL_3_UPPER + 1):
                self.LEDHandle[i] = (0,0,0)
        elif waterLevel == 4:
            for i in range(RESERVOIR_LEVEL_0_LOWER, RESERVOIR_LEVEL_3_UPPER + 1):
                self.LEDHandle[i] = LED_WATER_BLUE