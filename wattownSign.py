from values import LED_CITY_LIGHTS_YELLOW, LED_WATER_BLUE

class WattownSign():

    LED1_ADDRESS = 116
    LED2_ADDRESS = 117

    def __init__(self, LEDHandle):
        self.LEDHandle = LEDHandle

    def turnOn(self):
        self.LEDHandle[self.LED1_ADDRESS] = LED_CITY_LIGHTS_YELLOW
        self.LEDHandle[self.LED2_ADDRESS] = LED_WATER_BLUE

    def turnOff(self):
        self.LEDHandle[self.LED1_ADDRESS] = (0,0,0)
        self.LEDHandle[self.LED2_ADDRESS] = (0,0,0)