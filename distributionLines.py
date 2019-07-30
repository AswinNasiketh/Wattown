import values

class DistributionLine():

    ANIMATION_FRAME_RATE = 4 #changes per second

    def __init__(self, LEDHandle, startLEDAddress, numLEDs):
        self.LEDHandle = LEDHandle
        self.showPowerFlow = False

        self.timeOfLastChange = 0
        self.animationFramePeriod = 1000/DistributionLine.ANIMATION_FRAME_RATE #ms


        self.startLEDAddress = startLEDAddress
        self.numLEDs = numLEDs
        self.currentLEDAddress = startLEDAddress - 1 #to start on first LED

    def startPowerFlow(self):
        self.showPowerFlow = True
    
    def stopPowerFlow(self):
        self.showPowerFlow = False

    def update(self, currentTime):
        timeElapsed = currentTime - self.timeOfLastChange

        if self.showPowerFlow:
            if timeElapsed > self.animationFramePeriod:
                self.LEDHandle[self.currentLEDAddress] = (0,0,0)
                self.incrementLEDAddress()
                self.LEDHandle[self.currentLEDAddress] = values.LED_CITY_LIGHTS_YELLOW
        else:
            for i in range(self.numLEDs):
                self.LEDHandle[self.startLEDAddress + i] = (0,0,0)



    def incrementLEDAddress(self):
        self.currentLEDAddress += 1
        if self.currentLEDAddress >= self.startLEDAddress + self.numLEDs:
            self.currentLEDAddress = self.startLEDAddress

