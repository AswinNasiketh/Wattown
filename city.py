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
    def lightCityBlocks(self, blocksToLight, supplyTripped = False, offColourBlack = False):
        if offColourBlack:
            offColour = (0,0,0)
        else:
            offColour = LED_RED_DIM
        
        if blocksToLight == 0:
            self.setBlock1(offColour)
            self.setBlock2(offColour)
            self.setBlock3(offColour)

        elif blocksToLight == 1:
            self.setBlock1(LED_CITY_LIGHTS_YELLOW)
            self.setBlock2(offColour)
            self.setBlock3(offColour)
        elif blocksToLight == 2:
            self.setBlock1(LED_CITY_LIGHTS_YELLOW)
            self.setBlock2(LED_CITY_LIGHTS_YELLOW)
            self.setBlock3(offColour)
        elif blocksToLight == 3:
            self.setBlock1(LED_CITY_LIGHTS_YELLOW)
            self.setBlock2(LED_CITY_LIGHTS_YELLOW)
            
            if supplyTripped: # 3rd block is the only block affected by supply tripping
                self.setBlock3(LED_RED_DIM)
            else:
                self.setBlock3(LED_CITY_LIGHTS_YELLOW)
    
    #for more manual control
    def setCityLEDs(self, rangeLower, rangeUpper, colour):
        if rangeLower < City.BLOCK_1_LOWER or rangeUpper > City.BLOCK_3_UPPER:
            raise IndexError

        for i in range(rangeLower, rangeUpper + 1):
            self.LEDHandle[i] = colour
            
    def setBlock1(self, colour):
        for i in range(City.BLOCK_1_LOWER, City.BLOCK_1_UPPER + 1):
                self.LEDHandle[i] = colour
                
    def setBlock2(self, colour):
        for i in range(City.BLOCK_2_LOWER, City.BLOCK_2_UPPER + 1):
                self.LEDHandle[i] = colour
                
    def setBlock3(self, colour):
        for i in range(City.BLOCK_3_LOWER, City.BLOCK_3_UPPER + 1):
                self.LEDHandle[i] = colour
                
        
        
