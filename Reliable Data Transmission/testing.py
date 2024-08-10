'''
Name: Santosh Ramesh
Email: rameshsa@oregonstate.edu
Date: 5-24-22
Program: Reliable Data Transfer
Description: This is program sends data over an unreliable channel
'''

from ctypes import sizeof

from numpy import place
from segment import Segment


# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4 # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15 # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    dataRecieved = ''
    currentIteration = 0                                # Use this for segment 'timeouts'
    # Add items as needed

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        self.countSegmentTimeouts = 0
        self.timeIdle = 0
        self.processed = 0
        self.seqnum = "0"
        self.prevseq = 0
        self.acknum = "0"
        self.resend = False
        self.chars = 0
        # Add items as needed

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self,data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # Identify the data that has been received...

        # print('getDataReceived(): Complete this...')

        # ############################################################################################################ #
        dataToSend = self.dataRecieved
        # self.dataRecieved = ""

        return dataToSend

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):
        # segmentSend = Segment()

        # ############################################################################################################ #
        # print('processSend(): Complete this...')

        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters

        # Somewhere in here you will be creating data segments to send.
        # The data is just part of the entire string that you are trying to send.
        # The seqnum is the sequence number for the segment (in character number, not bytes)

        data = self.dataToSend[self.processed:]

        # ############################################################################################################ #
        # Display sending segment

        # Creating a packet to be sent
        self.chars = 0
        cont = True

        # Updating the data array and reseting the chars
        # self.dataToSend = self.dataToSend[chars:]
        # chars = 0

        while(cont):
            segmentSend = Segment()

            # Handles the special case where the pipeline window is smaller than the maximum data that can be sent in a segment
            if RDTLayer.DATA_LENGTH > RDTLayer.FLOW_CONTROL_WIN_SIZE:
                print("shopuldn't work")
                if len(data) > RDTLayer.FLOW_CONTROL_WIN_SIZE:
                    packet_data = data[:RDTLayer.FLOW_CONTROL_WIN_SIZE]
                    data = data[RDTLayer.FLOW_CONTROL_WIN_SIZE:]
                else:
                    packet_data = data
                    cont = False

            # If the string has more data left larger than the segment size
            elif len(data) > RDTLayer.DATA_LENGTH:
                
                # If the number of characters left remaining in the window is larger than the segment size
                if RDTLayer.FLOW_CONTROL_WIN_SIZE - self.chars > RDTLayer.DATA_LENGTH:
                    packet_data = data[:RDTLayer.DATA_LENGTH]
                    data = data[RDTLayer.DATA_LENGTH:]
                    self.chars = self.chars + len(packet_data)

                # If the number of characters left remaining in the window is less than the segment size
                else:
                    packet_data = data[:RDTLayer.FLOW_CONTROL_WIN_SIZE - self.chars]
                    data = data[RDTLayer.FLOW_CONTROL_WIN_SIZE - self.chars]
                    self.chars = self.chars + len(packet_data)
                    cont = False

            # If there is less than the length of segment size worth of characters left to send
            else:
                packet_data = data
                self.chars = self.chars + len(packet_data)
                cont = False

            # print("packet: [", packet_data, "]")
            self.seqnum = str(int(self.seqnum) + len(packet_data))
            segmentSend.setData(self.seqnum,packet_data)
            print("Sending segment: ", segmentSend.to_string())

            # Use the unreliable sendChannel to send the segment
            self.sendChannel.send(segmentSend)

        # self.dataToSend = self.dataToSend[chars:]
        if self.resend != True:
            self.processed = self.processed + self.chars
            print("processed:", self.processed)
        else:
            self.resend = True
            print("processed:", self.processed)
            self.processed = self.processed - self.chars
        self.chars = 0
        


    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        segmentAck = Segment()                  # Segment acknowledging packet(s) received

        # This call returns a list of incoming segments (see Segment class)...
        listIncomingSegments = self.receiveChannel.receive()

        # ############################################################################################################ #
        # What segments have been received?
        # How will you get them back in order?
        # This is where a majority of your logic will be implemented
        # print('processReceive(): Complete this...')

        # Somewhere in here you will be setting the contents of the ack segments to send.
        # The goal is to employ cumulative ack, just like TCP does...
        # print(listIncomingSegments)

        # ############################################################################################################ #
        # How do you respond to what you have received?
        # How can you tell data segments apart from ack segemnts?
        # print('processReceive(): Complete this...')

        # Sorting packets delievered out of order
        listIncomingSegments.sort(key=lambda x: int(x.seqnum))

        # Setting the first sent Ack to have the Ack number
        if len(listIncomingSegments) > 0:
            # print(" -   acknum: ", listIncomingSegments[0].acknum)
            # # self.acknum = listIncomingSegments[0].acknum
            # print(" -   seqnum: ", listIncomingSegments[0].seqnum)
            self.prevseq = int(listIncomingSegments[0].acknum)
        print("prev seq: ", self.prevseq)
        if self.prevseq + 15 != self.processed and self.processed != 0:
            self.resend = True

        # Sending an Ack for the segment to be resent if there is a dropped packet
        
        prev_seq = int(self.acknum)
        corrupt = False
        for seg in listIncomingSegments[1:]:
            if prev_seq + len(seg.payload) != int(seg.seqnum):
                print("=====")
                print("prev_seq, ", prev_seq)
                print("payload length ", len(seg.payload))
                print("seg.sum ", int(seg.seqnum))
                print("the previous packet got dropped")
                corrupt = True
                break
            prev_seq = int(seg.seqnum)
        
        # Adding the packets to the final "data recieved" variable which tracks what has been sent over
        if corrupt == False:
            for seg in listIncomingSegments[1:]:
                self.dataRecieved = self.dataRecieved + seg.payload
                self.acknum = seg.seqnum
        else:
            self.acknum = 0

 

        # ############################################################################################################ #
        # Display response segment
        segmentAck.setAck(self.acknum)
        print("Sending ack: ", segmentAck.to_string())

        # Use the unreliable sendChannel to send the ack packet
        self.sendChannel.send(segmentAck)
