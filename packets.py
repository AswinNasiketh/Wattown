#for substation Pi
import pyshark
from communication import sendCommand, WATTOWN_SERVER_SOCKET #use sendCommand to send requests to Wattown Pi
from threading import Thread, Event


class PacketSniffer(Thread):
    commandList = ['openSW1', 'closeSW1']

    def __init__(self):
        self.stopEvent = Event()
        self.stopEvent.clear()
        self.capture = pyshark.LiveCapture(interface='eth0')
        super().__init__()

    def run(self):
        for packet in self.capture.sniff_continuously():
            if self.stopEvent.is_set():
                break

            if self.isMMSPacket(packet):
                print("MMS Packet Found")
            elif self.isGOOSEPacket(packet):
                pass
                # print("GOOSE packet found")

    def isMMSPacket(self, packet):
        return 'MMS' in packet

    def isGOOSEPacket(self, packet):
        return 'GOOSE' in packet
    
    def getMMSLayerDetails(self, packet):
        print(packet.mms)

    def join(self, timeout = None):
        self.stopEvent.set()
        Thread.join(self, timeout)



#testing with pyshark and capture
# packets = pyshark.FileCapture('Wattown/mmsonly2.pcap')
# packets.set_debug()


# for packet in packets:
#     if 'IP' in packet:      
#         if 'MMS' in packet:
#             try:
#                 if packet.mms.confirmed_requestpdu_element != None :
#                     if packet.mms.itemId == 'DCCSWI3$CO$Pos$Oper':
#                         print("Switch operating packet found")
#                         print(packet.mms)
#                         input()
#             except AttributeError:
#                 print("AttributeError - requestPDU element doesn't exist - Ignore")
