from tkinter import *
from ui import *
import time
import threading

taskRunning = True

root = Tk()

app = Window(root)

def interactiveMode():
    t = threading.Thread(target=interactiveModeLoop)
    t.daemon = True
    t.start()

def interactiveModeLoop():
        print("Starting interactive mode")
        global taskRunning
        taskRunning = True
        app.setTaskRunning(taskRunning)
        while taskRunning:
                print("interactive mode running")
                taskRunning = app.getTaskRunning()
                time.sleep(1)

def dailyCycleMode():
    print("Starting daily cycle mode")

def gameMode():
    print("Starting game mode")

app.setInteractiveBtnCommand(interactiveMode)
app.setDailyCylceBtnCommand(dailyCycleMode)
app.setGameBtnCommand(gameMode)

root.mainloop()


