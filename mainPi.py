from tkinter import *
from wattownBoard import *
from ui import *
from interactiveMode import *
from cycleSim import *
import time
import threading

root = Tk()
mainWindow = MainWindow(root)
board = WattownBoard()

interactiveModeObj = InteractiveMode(mainWindow, board)

def interactiveMode():
    mainWindow.setTaskRunning(True, "Interactive Mode")
    runnerThread = threading.Thread(target = interactiveModeObj.interactiveModeLoop)
    runnerThread.daemon = True #ensures thread is killed when program closes
    runnerThread.start()

def cycleMode():
    newWindow = Toplevel(root)
    cycleModeSim = CycleSim(board, mainWindow)
    cycleModeConfigWindow = CycleModeControlsWindow(newWindow, cycleModeSim, mainWindow)

def gameMode():
    print("Game mode not implemented yet")

mainWindow.setInteractiveBtnCommand(interactiveMode)
mainWindow.setDailyCylceBtnCommand(cycleMode)
mainWindow.setGameBtnCommand(gameMode)

    
root.mainloop()
