from values import *

class City():
    BLOCK_1_LOWER = 12
    BLOCK_1_UPPER = 32
    BLOCK_2_LOWER = 33
    BLOCK_2_UPPER = 61
    BLOCK_3_LOWER = 62
    BLOCK_3_UPPER = 98

    def __init__(self, LEDHandle):
        self.LEDHandle = LEDHandle

    #blocksToLight can take values from 0 - 3
    def lightCityBlocks(self, blocksToLight, supplyTripped = False):
        if blocksToLight == 0:            
            for i in range(City.BLOCK_1_LOWER, City.BLOCK_3_UPPER + 1):
                self.LEDHandle[i] = LED_RED_DIM

        elif blocksToLight == 1:
            for i in range(City.BLOCK_1_LOWER, City.BLOCK_1_UPPER + 1):
                if supplyTripped and (i % 2):#if the supply is tripped, set all odd LEDs to red
                    self.LEDHandle[i] = LED_RED_DIM
                else:
                    self.LEDHandle[i] = LED_CITY_LIGHTS_YELLOW
                
            for i in range(City.BLOCK_2_LOWER, City.BLOCK_3_UPPER + 1):
                self.LEDHandle[i] = (0,0,0)
        elif blocksToLight == 2:
            for i in range(City.BLOCK_1_LOWER, City.BLOCK_2_UPPER + 1):
                if supplyTripped and (i % 2):
                    self.LEDHandle[i] = LED_RED_DIM
                else:
                    self.LEDHandle[i] = LED_CITY_LIGHTS_YELLOW
                
            for i in range(City.BLOCK_3_LOWER, City.BLOCK_3_UPPER + 1):
                self.LEDHandle[i] = (0,0,0)
        elif blocksToLight == 3:
            for i in range(City.BLOCK_1_LOWER, City.BLOCK_3_UPPER + 1):
                if supplyTripped and (i % 2):
                    self.LEDHandle[i] = LED_RED_DIM
                else:
                    self.LEDHandle[i] = LED_CITY_LIGHTS_YELLOW
    
    #for more manual control
    def setCityLEDs(self, rangeLower, rangeUpper, colour):
        if rangeLower < City.BLOCK_1_LOWER or rangeUpper > City.BLOCK_3_UPPER:
            raise IndexError

        for i in range(rangeLower, rangeUpper + 1):
            self.LEDHandle[i] = colour