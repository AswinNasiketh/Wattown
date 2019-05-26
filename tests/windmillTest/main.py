from tkinter import *
from wattownBoard import *
from ui import *

board = WattownBoard()

root = Tk()

window = WindmillTestWindow(board, root)

root.mainloop()

board.resetBoard()
board.releaseResources()
