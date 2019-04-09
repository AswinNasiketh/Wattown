from tkinter import *
from tkinter.ttk import *


class WindmillTestWindow(Frame):

    def __init__(self, board, master = None):
        Frame.__init__(self, master)
        self.master = master
        self.board = board
        self.initWindow()

    def initWindow(self):

        self.master.title("Wattown Windmill Test")

        self.pack(fill=BOTH, expand =1)

        self.statusLabel = Label(self, text="Windmills Stopped")
        self.statusLabel.pack(side=LEFT)

        frequencyScaleContainer = Frame(self)

        self.frequency = DoubleVar()

        frequencyScaleLabel = Label(frequencyScaleContainer, text = "Driving Frequency")
        frequencyScaleLabel.pack(side=LEFT)

        frequencyScale = Scale(frequencyScaleContainer, orient=HORIZONTAL, from_=6, to=20, variable = self.frequency, command = self.updateFrequencyDisplay)
        frequencyScale.pack(side=LEFT)

        self.frequencyDisplayLabel = Label(frequencyScaleContainer, text = "4Hz")
        self.frequencyDisplayLabel.pack(side=LEFT)

        frequencyScaleContainer.pack(padx= 8, pady = 8)

        driveWindmillsButton = Button(self, text="Drive Windmills", command = self.driveWindmills)
        driveWindmillsButton.pack(side = LEFT)

        stopWindmillsButton = Button(self, text="Stop Windmills", command = self.stopWindmills)
        stopWindmillsButton.pack(side=LEFT)         

        


    def updateFrequencyDisplay(self, frequency):
        intFrequency = int(float(frequency))
        self.frequencyDisplayLabel.configure(text = str(intFrequency) + "Hz")

    
    def driveWindmills(self):
        intFrequency = int(self.frequency.get())
        self.board.driveWindmills(intFrequency)
        self.statusLabel.configure(text="Driving Windmills at: " + str(intFrequency) + "Hz")

    def stopWindmills(self):
        self.board.stopWindmills()
        self.statusLabel.configure(text="Windmills Stopped")
