from values import *

class City():

    CITY_BLOCK_1_LOWER = 12
    CITY_BLOCK_1_UPPER = 32
    CITY_BLOCK_2_LOWER = 33
    CITY_BLOCK_2_UPPER = 61
    CITY_BLOCK_3_LOWER = 62
    CITY_BLOCK_3_UPPER = 98

    def __init__(self, LEDHandle):
        self.LEDHandle = LEDHandle

    #blocksToLight can take values from 0 - 3
    def lightCityBlocks(self, blocksToLight):
        if blocksToLight == 0:            
            for i in range(CITY_BLOCK_1_LOWER, CITY_BLOCK_3_UPPER):
                self.LEDHandle[i] = LED_RED_DIM

        elif blocksToLight == 1:
            for i in range(CITY_BLOCK_1_LOWER, CITY_BLOCK_1_UPPER):
                self.LEDHandle[i] = LED_CITY_LIGHTS_YELLOW
                
            for i in range(CITY_BLOCK_2_LOWER, CITY_BLOCK_3_UPPER):
                self.LEDHandle[i] = (0,0,0)
        elif blocksToLight == 2:
            for i in range(CITY_BLOCK_1_LOWER, CITY_BLOCK_2_UPPER):
                self.LEDHandle[i] = LED_CITY_LIGHTS_YELLOW
                
            for i in range(CITY_BLOCK_3_LOWER, CITY_BLOCK_3_UPPER):
                self.LEDHandle[i] = (0,0,0)
        elif blocksToLight == 3:
            for i in range(CITY_BLOCK_1_LOWER, CITY_BLOCK_3_UPPER):
                self.LEDHandle[i] = LED_CITY_LIGHTS_YELLOw
    
    #for more manual control
    def setCityLEDs(self, rangeLower, rangeUpper, colour):
        if rangeLower < CITY_BLOCK_1_LOWER or rangeUpper > CITY_BLOCK_3_UPPER:
            raise IndexError

        for i in range(rangeLower, rangeUpper):
            self.LEDHandle[i] = colour