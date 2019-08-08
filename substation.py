from values import LED_GREEN_BRIGHT, LED_RED_DIM

class Substation():

    #need to assign real substation functions to each LED
    LED1_ADDR = 110
    LED2_ADDR = 111
    LED3_ADDR = 112


    def __init__(self, LEDHandle):
        self.LEDHandle = LEDHandle

    def setLED(self, address, onState):
        if onState:
            self.LEDHandle[address] = LED_GREEN_BRIGHT
        else:
            self.LEDHandle[address] = LED_RED_DIM
    
    #for non substation modes        
    def setLEDsGreen(self):
        self.setLED(self.LED1_ADDR, True)
        self.setLED(self.LED2_ADDR, True)
        self.setLED(self.LED3_ADDR, True)
