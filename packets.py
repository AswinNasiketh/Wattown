#for substation Pi
import pyshark
from communication import sendCommand, WATTOWN_SERVER_SOCKET #use sendCommand to send requests to Wattown Pi
from threading import Thread, Event
import logging

logging.basicConfig(level = logging.INFO)


class PacketSniffer(Thread):
    commandList = ['openSW1', 'closeSW1']

    def __init__(self):
        self.stopEvent = Event()
        self.stopEvent.clear()
        self.capture = pyshark.LiveCapture(interface='eth0', custom_parameters = {"-C": "tshark-mms"})
        #self.capture.set_debug()
        Thread.__init__(self,daemon=True)

    def run(self):
        for packet in self.capture.sniff_continuously():
            if self.stopEvent.is_set():
                break
            #print(packet)
            if self.isMMSPacket(packet):
                logging.debug("MMS Packet found")
                commandToSend = self.parseMMSPacket(packet)
                if commandToSend != -1:
                    result = sendCommand(WATTOWN_SERVER_SOCKET, self.commandList[commandToSend])
                    if result:
                        logging.info("command sent successfully!")
                    else:
                        logging.info("command send failed")
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
                            return 1
                        else:
                            logging.info("Open Switch")
                            return 0
            return -1
        except AttributeError:
            logging.debug("AttributeError - requestPDU element doesn't exist - Ignore")
            return -1

#testing with scapy and packet spoofing
#for testing substation mode Pi's reactions, just change pcap file
# from scapy.all import *

# packets = rdpcap('openQB2.pcapng')
# input()

# for packet in packets:
#     if IP in packet:
#         packet[IP].dst = '172.19.6.1'
#         del packet[IP].chksum
#     if TCP in packet:
#         del packet[TCP].chksum


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
