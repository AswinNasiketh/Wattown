from tkinter import *
from wattownBoard import *
from ui import *
from interactiveMode import *
import time
import threading

root = Tk()
app = Window(root)
board = WattownBoard()

interactiveModeObj = InteractiveMode(app, board)

def interactiveMode():
    app.setTaskRunning(True, "Interactive Mode")
    runnerThread = threading.Thread(target = interactiveModeObj.interactiveModeLoop)
    runnerThread.daemon = True
    runnerThread.start()

def cycleMode():
    pass

def gameMode():
    pass

app.setInteractiveBtnCommand(interactiveMode)
app.setDailyCylceBtnCommand(cycleMode)
app.setGameBtnCommand(gameMode)

root.mainloop()