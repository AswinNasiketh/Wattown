from tkinter import *
from ui import *

def interactiveMode():
    print("Starting interactive mode")

def dailyCycleMode():
    print("Starting daily cycle mode")

def gameMode():
    print("Starting game mode")



root = Tk()
# root.geometry("400x300")

app = Window(interactiveMode, dailyCycleMode, gameMode, root)

root.mainloop()


