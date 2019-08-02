from wattownBoard import *

board = WattownBoard()

board.lightCityBlocks(1)
board.lightReservoir(100)

board.driveWindmills()

input()
board.stopWindmills()

board.resetBoard()

board.releaseResources()

