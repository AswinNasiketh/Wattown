#for substation pi
from packets import *

sniffer = PacketSniffer()
print("Starting sniffing")
sniffer.run() #have sniffer running in main thread for now
