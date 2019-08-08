#for substation Pi
import pyshark
from communication import sendCommand, WATTOWN_SERVER_SOCKET #use sendCommand to send requests to Wattown Pi
from threading import Thread, Event
import logging

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
                commandToSend = self.parseMMSPacket(packet)
                if commandToSend != -1:
                    sendCommand(WATTOWN_SERVER_SOCKET, self.commandList[commandToSend])
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

    #returns index of command to send in command list, -1 if packet not related to any command
    def parseMMSPacket(self, packet):    
        try:
            if packet.mms.confirmed_requestpdu_element != None :
                if "Q07" in packet.mms.domainId:
                    logging.info("Packet for Q07 found")
                    if "Pos$SBOw" in packet.mms.itemId:
                        logging.info("Switch Select packet found")
                        logging.info("Switch selected: %s", str(packet.mms.itemId).split('$')[0])#get substring right before first '$'
                    elif "Pos$Oper" in packet.mms.itemId:
                        logging.info("Switch operate packet found")
                        closedVal = int(packet.mms.boolean)
                        if closedVal == 1:
                            logging.info("Close switch")
                            return 0
                        else:
                            logging.info("Open Switch")
                            return 1
            return -1
        except AttributeError:
            logging.debug("AttributeError - requestPDU element doesn't exist - Ignore")


#testing with scapy and packet spoofing

# from scapy.all import *

# packets = rdpcap('Wattown/packetCaptures/openQB2.pcapng')
# input()
# sendp(packets, iface='Realtek USB GbE Family Controller #2')



# testing with pyshark and capture
# packets = pyshark.FileCapture('Wattown/packetCaptures/openQB2.pcapng')
# packets.set_debug()
# logging.basicConfig(level=logging.INFO)


# for packet in packets:
#     if 'IP' in packet:      
#         if 'MMS' in packet:
#             try:
#                 if packet.mms.confirmed_requestpdu_element != None :
#                     if "Q07" in packet.mms.domainId:
#                         logging.info("Packet for Q07 found")
#                         if "Pos$SBOw" in packet.mms.itemId:
#                             logging.info("Switch Select packet found")
#                             logging.info("Switch selected: %s", str(packet.mms.itemId).split('$')[0])
#                         elif "$Pos$Oper" in packet.mms.itemId:
#                             logging.info("Switch operate packet found")
#                             closedVal = int(packet.mms.boolean)
#                             if closedVal == 1:
#                                 logging.info("Close switch")
#                             else:
#                                 logging.info("Open Switch")
#             except AttributeError:
#                 logging.debug("AttributeError - requestPDU element doesn't exist - Ignore")
