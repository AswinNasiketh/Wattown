from tkinter import *
from wattownBoard import WattownBoard
from ui import MainWindow
import matplotlib as mpl
import values
from plotting import GraphsProcessManager



def gameMode():
    # newWindow = Toplevel(root)
    # gameModeConfigWindow = GameModeParametersWindow(newWindow, board, mainWindow, root)
    print("Not fully implemented!")



    



def main():
    mpl.rcParams['toolbar'] = 'None'
    
    board = WattownBoard()
    board.start()

    graphProcessManager = GraphsProcessManager()
    graphProcessManager.configure(values.GRAPH_MAX_POWER, values.GRAPH_MIN_POWER, values.GRAPH_MAX_CONS, values.GRAPH_MIN_CONS)
    graphProcessManager.startPlotting()
    graphProcessManager.hidePlots()

    root = Tk()
    mainWindow = MainWindow(board, graphProcessManager, root)

    mainWindow.setGameBtnCommand(gameMode)

    root.mainloop()

    board.join()
    board.releaseResources()
    graphProcessManager.stopPlotting()


if __name__ == "__main__":
    main()
