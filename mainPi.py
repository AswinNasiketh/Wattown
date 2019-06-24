from tkinter import *
from wattownBoard import WattownBoard
from ui import MainWindow
import time
import threading
import matplotlib as mpl

mpl.rcParams['toolbar'] = 'None' 

root = Tk()
board = WattownBoard()

mainWindow = MainWindow(board, root)

def gameMode():
    # newWindow = Toplevel(root)
    # gameModeConfigWindow = GameModeParametersWindow(newWindow, board, mainWindow, root)
    print("Not fully implemented!")

mainWindow.setGameBtnCommand(gameMode)

    
root.mainloop()

board.resetBoard()
board.releaseResources()
