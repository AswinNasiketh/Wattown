class TransmissionLines():

    LEFT_TOWER_ADDRESS = 14
    MIDDLE_TOWER_ADDRESS = 15
    RIGHT_TOWER_ADDRESS = 16

    def __init__(self, LEDHandle):
        self.LEDHandle = LEDHandle

    def setLeftTowerColour(self, colour):
        self.LEDHandle[TransmissionLines.LEFT_TOWER_ADDRESS] = colour

    def setMiddleTowerColour(self, colour):
        self.LEDHandle[TransmissionLines.MIDDLE_TOWER_ADDRESS] = colour

    def setRightTowerColour(self, colour):
        self.LEDHandle[TransmissionLines.RIGHT_TOWER_ADDRESS] = colour

    def setAllTowersColour(self, colour):
        self.setLeftTowerColour(colour)
        self.setMiddleTowerColour(colour)
        self.setRightTowerColour(colour)
    
