from tkinter import *
from ui import *
import time
import threading

# taskRunning = True

root = Tk()

simulation = 5
mainWindow = MainWindow(root)
newWin = Toplevel(root)
app = CycleModeControlsWindow(newWin, 5, mainWindow)


# def interactiveMode():
#     t = threading.Thread(target=interactiveModeLoop)
#     t.daemon = True
#     t.start()

# def interactiveModeLoop():
#         print("Starting interactive mode")
#         global taskRunning
#         taskRunning = True
#         app.setTaskRunning(taskRunning, "Interactive Mode")
#         while taskRunning:
#                 print("interactive mode running")
#                 taskRunning = app.getTaskRunning()
#                 time.sleep(1)

# def dailyCycleMode():
#     print("daily cycle mode not implemented")

# def gameMode():
#     print("game mode not implemented")

# app.setInteractiveBtnCommand(interactiveMode)
# app.setDailyCylceBtnCommand(dailyCycleMode)
# app.setGameBtnCommand(gameMode)

root.mainloop()


