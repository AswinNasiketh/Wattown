class DistributionLine():

    FAST_ANIMATION_FRAME_RATE = 5 #changes per second
    SLOW_ANIMATION_FRAME_RATE = 4

    def __init__(self, LEDHandle, startLEDAddress, numLEDs, reversed = False):
        self.LEDHandle = LEDHandle
        self.showPowerFlow = False

        self.timeOfLastChange = 0
        self.animationFramePeriod = 1000/DistributionLine.FAST_ANIMATION_FRAME_RATE #ms

        self.startLEDAddress = startLEDAddress
        self.numLEDs = numLEDs
        self.reversed = reversed

        if reversed:
            self.currentLEDAddress = startLEDAddress + numLEDs - 1
        else:            
            self.currentLEDAddress = startLEDAddress #ignore that it will start on second LED

    def startPowerFlow(self):
        self.showPowerFlow = True
    
    def stopPowerFlow(self):
        self.showPowerFlow = False

    def update(self, currentTime):
        timeElapsed = currentTime - self.timeOfLastChange

        if self.showPowerFlow:
            if timeElapsed > self.animationFramePeriod:
                self.LEDHandle[self.currentLEDAddress] = (0,0,0)
                
                if self.reversed:
                    self.decrementLEDAddress()
                else:
                    self.incrementLEDAddress()

                self.LEDHandle[self.currentLEDAddress] = (50,50,50)
                self.timeOfLastChange = currentTime
        else:
            for i in range(self.numLEDs):
                self.LEDHandle[self.startLEDAddress + i] = (0,0,0)

    def setFrameRate(self, frameRate):
        self.animationFramePeriod = 1000/frameRate

    def incrementLEDAddress(self):
        self.currentLEDAddress += 1
        if self.currentLEDAddress >= self.startLEDAddress + self.numLEDs:
            self.currentLEDAddress = self.startLEDAddress

    def decrementLEDAddress(self):
        self.currentLEDAddress -= 1
        if self.currentLEDAddress < self.startLEDAddress:
            self.currentLEDAddress = self.startLEDAddress + self.numLEDs - 1 
