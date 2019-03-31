from tkinter import *

class Window(Frame):
    
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.taskRunning = False
        self.initWindow()

    def initWindow(self):

        self.master.title("Wattown Board Controller")

        self.pack(fill=BOTH, expand =1)

        self.statusLabel = Label(self, text = "Status = Idle")
        self.statusLabel.pack(fill = X, expand = 1)

        self.interactiveModeButton = Button(self, text = "Start interactive mode")
        self.interactiveModeButton.pack(fill=X, expand =1)

        self.dailyCycleModeButton = Button(self, text = "Start Daily Cycle Mode")
        self.dailyCycleModeButton.pack(fill = X, expand =1)

        self.gameModeButton = Button(self, text = "Start Game Mode")
        self.gameModeButton.pack(fill = X, expand =1)

        stopButton = Button(self, text = "Stop Current Activity", command = self.stopCurrentActivity)
        stopButton.pack(fill = X, expand =1)

    def setInteractiveBtnCommand(self, interactiveButtonFunction):
        self.interactiveModeButton.configure(command = interactiveButtonFunction)
    
    def setDailyCylceBtnCommand(self, dailyCylcleButtonFunction):
        self.dailyCycleModeButton.configure(command = dailyCylcleButtonFunction)

    def setGameBtnCommand(self, gameButtonCommand):
        self.gameModeButton.configure(command = gameButtonCommand)


    def stopCurrentActivity(self):
        print("stopping activity")
        self.taskRunning = False
        self.statusLabel.configure(text = "Status: Idle")

    def getTaskRunning(self): #TODO: use this as global safety to not run two tasks at the same time
        return self.taskRunning        
    
    def setTaskRunning(self, taskRunning, taskDescription = "Idle"):
        self.taskRunning = taskRunning
        if taskRunning:
            self.statusLabel.configure(text = "Status: Running " + taskDescription)
        else:
            self.statusLabel.configure(text = "Status: Idle")
     


