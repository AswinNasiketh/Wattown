import matplotlib.pyplot as plt
from plotting import *
import time

one = 1
mpl.rcParams['toolbar'] = 'None' 

fig = plt.figure(figsize=(15, 15), dpi=80)
plt.subplots_adjust(hspace=0.4)

powerPlotter = PowerGraph()
powerPlotter.configure(5, -2)
powerPlotter.setupFigure(fig)

supplyPlotter = ConsumptionSupplyGraph()
supplyPlotter.configure(10, -10)
supplyPlotter.setupFigure(fig)

storagePlotter = StoredEnergyGraph()
storagePlotter.setupFigure(fig)

plt.ion()
plt.show()


for i in range(0, 10):
    one = -one
    powerPlotter.setPowers(i*0.2, i*0.1, one)

    supplyPlotter.setConsumption(i*0.4)
    supplyPlotter.setRenewableSupply(i*0.5)

    batteryEnergy = 10 - i
    reservoirEnergy = 100 - (5*i)
    storagePlotter.setRemainingEnergies(batteryEnergy, reservoirEnergy)   

    powerPlotter.animate()
    supplyPlotter.animate()
    storagePlotter.animate()

    plt.pause(0.001)
    time.sleep(0.5)

#need to plot:
# windpower
# solarpower
# reservoirpower

# consumption
# renewable surplus/lack

# reservoir energy
# battery energy

# labels = ["Wind Power", "Solar Power", "Hydro Power"]

# values = [1, 2, 3]
# index = [1, 2, 3]

# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1)

# def animate(i):
#     values = [i , i/2 , i/4]

#     ax.clear()
#     ax.bar(index, values)
#     ax.set_xlabel("Power Source")
#     ax.set_ylabel("Power Generation this hour (GW)")
#     ax.set_xticks(index)
#     ax.set_xticklabels(labels)
    

# ani = animation.FuncAnimation(fig, animate, interval =1000)
# plt.show()