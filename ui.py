from tkinter import *

class Window(Frame):
    
    def __init__(self, interactiveModeFunction, dailyCycleModeFunction, gameModeFunction, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.interactiveMode = interactiveModeFunction
        self.dailyCycleMode = dailyCycleModeFunction
        self.gameModeFunction = gameModeFunction
        self.initWindow()

    def initWindow(self):

        self.master.title("Wattown Board Controller")

        self.pack(fill=BOTH, expand =1)

        interactiveModeButton = Button(self, text = "Start interactive mode", command = self.interactiveMode)
        interactiveModeButton.pack(fill=X, expand =1)

        dailyCycleModeButton = Button(self, text = "Start Daily Cycle Mode", command = self.dailyCycleMode)
        dailyCycleModeButton.pack(fill = X, expand =1)

        gameModeButton = Button(self, text = "Start Game Mode", command = self.gameModeFunction)
        gameModeButton.pack(fill = X, expand =1)


