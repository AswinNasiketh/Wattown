#for testing on Windows

# from tkinter import *
# from ui import *
# import time
# import threading

# # taskRunning = True

# root = Tk()

# simulation = 5
# mainWindow = MainWindow(root)
# newWin = Toplevel(root)
# app = CycleModeControlsWindow(newWin, 5, mainWindow)


# # def interactiveMode():
# #     t = threading.Thread(target=interactiveModeLoop)
# #     t.daemon = True
# #     t.start()

# # def interactiveModeLoop():
# #         print("Starting interactive mode")
# #         global taskRunning
# #         taskRunning = True
# #         app.setTaskRunning(taskRunning, "Interactive Mode")
# #         while taskRunning:
# #                 print("interactive mode running")
# #                 taskRunning = app.getTaskRunning()
# #                 time.sleep(1)

# # def dailyCycleMode():
# #     print("daily cycle mode not implemented")

# # def gameMode():
# #     print("game mode not implemented")

# # app.setInteractiveBtnCommand(interactiveMode)
# # app.setDailyCylceBtnCommand(dailyCycleMode)
# # app.setGameBtnCommand(gameMode)

# root.mainloop()

from plotting import GraphsProcessManager
import time

def main():
    graphs = GraphsProcessManager()

    graphs.configure(10, -2, 7, -5)
    graphs.startPlotting()

    for i in range(10):
        if i % 2 == 1:
            supply = 3
            demand = 4
            solar = 7
            wind = 3
            hydro = 5
            battery = 70
            resrevoir = 20
        else:
            supply = 6
            demand = 1
            solar = 4
            wind = 5
            hydro = 2
            battery = 60
            resrevoir = 30

        graphs.setRenewablePowers(solar, wind, hydro)
        graphs.setSupplyDemand(supply, demand)
        graphs.setStoredEnergy(battery, resrevoir)

        time.sleep(1.0)

    graphs.stopPlotting()

if __name__ == '__main__':
    main()

