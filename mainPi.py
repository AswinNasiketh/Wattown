from tkinter import *
from wattownBoard import *
from ui import *
from interactiveMode import *
import time
import threading

root = Tk()
app = MainWindow(root)
board = WattownBoard()

interactiveModeObj = InteractiveMode(app, board)

def interactiveMode():
    app.setTaskRunning(True, "Interactive Mode")
    runnerThread = threading.Thread(target = interactiveModeObj.interactiveModeLoop)
    runnerThread.daemon = True #ensures thread is killed when program closes
    runnerThread.start()

def cycleMode():
    print("Cycle mode not implemented yet")

def gameMode():
    print("Game mode not implemented yet")

app.setInteractiveBtnCommand(interactiveMode)
app.setDailyCylceBtnCommand(cycleMode)
app.setGameBtnCommand(gameMode)

root.mainloop()