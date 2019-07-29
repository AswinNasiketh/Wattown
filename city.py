from values import *

class City():

    #TODO: change LED addresses to include added transmission network and distribution network LEDs

    BLOCK_1_LOWER = 25
    BLOCK_1_UPPER = 45
    BLOCK_2_LOWER = 46
    BLOCK_2_UPPER = 74
    BLOCK_3_LOWER = 75
    BLOCK_3_UPPER = 111

    def __init__(self, LEDHandle):
        self.LEDHandle = LEDHandle

    #blocksToLight can take values from 0 - 3
    def lightCityBlocks(self, blocksToLight):
        if blocksToLight == 0:            
            for i in range(City.BLOCK_1_LOWER, City.BLOCK_3_UPPER + 1):
                self.LEDHandle[i] = LED_RED_DIM

        elif blocksToLight == 1:
            for i in range(City.BLOCK_1_LOWER, City.BLOCK_1_UPPER + 1):
                self.LEDHandle[i] = LED_CITY_LIGHTS_YELLOW
                
            for i in range(City.BLOCK_2_LOWER, City.BLOCK_3_UPPER + 1):
                self.LEDHandle[i] = (0,0,0)
        elif blocksToLight == 2:
            for i in range(City.BLOCK_1_LOWER, City.BLOCK_2_UPPER + 1):
                self.LEDHandle[i] = LED_CITY_LIGHTS_YELLOW
                
            for i in range(City.BLOCK_3_LOWER, City.BLOCK_3_UPPER + 1):
                self.LEDHandle[i] = (0,0,0)
        elif blocksToLight == 3:
            for i in range(City.BLOCK_1_LOWER, City.BLOCK_3_UPPER + 1):
                self.LEDHandle[i] = LED_CITY_LIGHTS_YELLOW
    
    #for more manual control
    def setCityLEDs(self, rangeLower, rangeUpper, colour):
        if rangeLower < City.BLOCK_1_LOWER or rangeUpper > City.BLOCK_3_UPPER:
            raise IndexError

        for i in range(rangeLower, rangeUpper + 1):
            self.LEDHandle[i] = colour