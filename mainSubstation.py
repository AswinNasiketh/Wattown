#for substation pi
from packets import *

sniffer = PacketSniffer()
print("Starting sniffing")
sniffer.start()