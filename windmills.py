import time

class Windmills():

    DRIVE_FREQUENCY = 4 #Hz
    DRIVE_POSITIVE_PIN = 1
    DRIVE_NEGATIVE_PIN = 7

    def __init__(self, pigpioHandle):
        self.pi = pigpioHandle
        self.driveWindmills = False
        self.timeSinceLastUpdate = self.getTimeMilliseconds()
        self.halfPeriod = 1000/DRIVE_FREQUENCY

    def startWindmills(self):
        self.driveWindmills = True
        self.positivePinOn = False

    def stopWindmills(self):
        self.driveWindmills = False

    def update(self):       
        if self.driveWindmills:
            timeElapsed = getTimeMilliseconds() - self.timeSinceLastUpdate


            if timeElapsed >= self.halfPeriod:
                if self.positivePinOn:
                    self.pi.write(DRIVE_POSITIVE_PIN, 0)
                    self.pi.write(DRIVE_NEGATIVE_PIN, 1)
                    self.positivePinOn = False
                else:
                    self.pi.write(DRIVE_POSITIVE_PIN, 1)
                    self.pi.write(DRIVE_NEGATIVE_PIN, 0)
                    self.positivePinOn = True

        else:
            self.pi.write(DRIVE_POSITIVE_PIN, 0)
            self.pi.write(DRIVE_NEGATIVE_PIN, 0)     

        self.timeSinceLastUpdate = getTimeMilliseconds()              

    def getTimeMilliseconds(self):
        return int(round(time.time() * 1000))


    