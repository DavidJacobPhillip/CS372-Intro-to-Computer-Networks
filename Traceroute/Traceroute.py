'''
Name: Santosh Ramesh
Email: rameshsa@oregonstate.edu
Date: 5-4-22
Program: Traceroute
Description: This program sends ICMP echos and traceroutes the packets
'''

# Sources Used:
# - https://www.programcreek.com/python/example/81627/scapy.all.ICMP
# - https://datagy.io/python-print-objects-attributes/#:~:text=an%20object's%20attributes.-,Use%20Python's%20vars()%20to%20Print%20an%20Object's%20Attributes,use%20the%20vars()%20function.
# - https://www.kadiska.com/blog-using-traceroute-to-measure-network-latency-and-packet-loss/
# - https://www.geeksforgeeks.org/difference-between-ping-and-traceroute/
# - https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml      
# - ttp://www.networksorcery.com/enp/protocol/icmp/msg0.htm  
# - https://www.techtarget.com/searchnetworking/answer/How-to-test-for-packet-loss-on-a-broadband-connection
# - https://www.computernetworkingnotes.com/networking-tutorials/icmp-error-messages-and-format-explained.html
# - https://www.iana.org/assignments/icmp-parameters/icmp-parameters.xhtml#icmp-parameters-codes-0

# Imports                                                                                                              #
from functools import total_ordering
import os
from socket import *
import struct
import time
import select
import sys

# Globals
total_RTT = 0
min_RTT = 100000000000
max_RTT = 0
total_data = 0
packet_loss = 0
packets_sent = 0

# Class IcmpHelperLibrary                                                                                              
class IcmpHelperLibrary:

    # Class IcmpPacket                                                                                                                                                                                                             
    class IcmpPacket:
        # IcmpPacket Class Scope Variables                                                                             
        __icmpTarget = ""               # Remote Host
        __destinationIpAddress = ""     # Remote Host IP Address
        __header = b''                  # Header after byte packing
        __data = b''                    # Data after encoding
        __dataRaw = ""                  # Raw string data before encoding
        __icmpType = 0                  # Valid values are 0-255 (unsigned int, 8 bits)
        __icmpCode = 0                  # Valid values are 0-255 (unsigned int, 8 bits)
        __packetChecksum = 0            # Valid values are 0-65535 (unsigned short, 16 bits)
        __packetIdentifier = 0          # Valid values are 0-65535 (unsigned short, 16 bits)
        __packetSequenceNumber = 0      # Valid values are 0-65535 (unsigned short, 16 bits)
        __ipTimeout = 30
        __ttl = 255                     # Time to live

        __DEBUG_IcmpPacket = False      # Allows for debug output

        # IcmpPacket Class Getters                                                                                     
        def getIcmpTarget(self):
            return self.__icmpTarget

        def getDataRaw(self):
            return self.__dataRaw

        def getIcmpType(self):
            return self.__icmpType

        def getIcmpCode(self):
            return self.__icmpCode

        def getPacketChecksum(self):
            return self.__packetChecksum

        def getPacketIdentifier(self):
            return self.__packetIdentifier

        def getPacketSequenceNumber(self):
            return self.__packetSequenceNumber

        def getTtl(self):
            return self.__ttl

        # IcmpPacket Class Setters                                                                                     
        def setIcmpTarget(self, icmpTarget):
            self.__icmpTarget = icmpTarget

            # Only attempt to get destination address if it is not whitespace
            if len(self.__icmpTarget.strip()) > 0:
                self.__destinationIpAddress = gethostbyname(self.__icmpTarget.strip())

        def setIcmpType(self, icmpType):
            self.__icmpType = icmpType

        def setIcmpCode(self, icmpCode):
            self.__icmpCode = icmpCode

        def setPacketChecksum(self, packetChecksum):
            self.__packetChecksum = packetChecksum

        def setPacketIdentifier(self, packetIdentifier):
            self.__packetIdentifier = packetIdentifier

        def setPacketSequenceNumber(self, sequenceNumber):
            self.__packetSequenceNumber = sequenceNumber

        def setTtl(self, ttl):
            self.__ttl = ttl

        # IcmpPacket Class Private Functions                                                                           
        def __recalculateChecksum(self):
            print("calculateChecksum Started...") if self.__DEBUG_IcmpPacket else 0
            packetAsByteData = b''.join([self.__header, self.__data])
            checksum = 0

            # This checksum function will work with pairs of values with two separate 16 bit segments. Any remaining
            # 16 bit segment will be handled on the upper end of the 32 bit segment.
            countTo = (len(packetAsByteData) // 2) * 2

            # Calculate checksum for all paired segments
            print(f'{"Count":10} {"Value":10} {"Sum":10}') if self.__DEBUG_IcmpPacket else 0
            count = 0
            while count < countTo:
                thisVal = packetAsByteData[count + 1] * 256 + packetAsByteData[count]
                checksum = checksum + thisVal
                checksum = checksum & 0xffffffff        # Capture 16 bit checksum as 32 bit value
                print(f'{count:10} {hex(thisVal):10} {hex(checksum):10}') if self.__DEBUG_IcmpPacket else 0
                count = count + 2

            # Calculate checksum for remaining segment (if there are any)
            if countTo < len(packetAsByteData):
                thisVal = packetAsByteData[len(packetAsByteData) - 1]
                checksum = checksum + thisVal
                checksum = checksum & 0xffffffff        # Capture as 32 bit value
                print(count, "\t", hex(thisVal), "\t", hex(checksum)) if self.__DEBUG_IcmpPacket else 0

            # Add 1's Complement Rotation to original checksum
            checksum = (checksum >> 16) + (checksum & 0xffff)   # Rotate and add to base 16 bits
            checksum = (checksum >> 16) + checksum              # Rotate and add

            answer = ~checksum                  # Invert bits
            answer = answer & 0xffff            # Trim to 16 bit value
            answer = answer >> 8 | (answer << 8 & 0xff00)
            print("Checksum: ", hex(answer)) if self.__DEBUG_IcmpPacket else 0

            self.setPacketChecksum(answer)

        def __packHeader(self):
            # The following header is based on http://www.networksorcery.com/enp/protocol/icmp/msg8.htm
            # Type = 8 bits
            # Code = 8 bits
            # ICMP Header Checksum = 16 bits
            # Identifier = 16 bits
            # Sequence Number = 16 bits
            self.__header = struct.pack("!BBHHH",
                                   self.getIcmpType(),              #  8 bits / 1 byte  / Format code B
                                   self.getIcmpCode(),              #  8 bits / 1 byte  / Format code B
                                   self.getPacketChecksum(),        # 16 bits / 2 bytes / Format code H
                                   self.getPacketIdentifier(),      # 16 bits / 2 bytes / Format code H
                                   self.getPacketSequenceNumber()   # 16 bits / 2 bytes / Format code H
                                   )

        def __encodeData(self):
            data_time = struct.pack("d", time.time())               # Used to track overall round trip time
                                                                    # time.time() creates a 64 bit value of 8 bytes
            dataRawEncoded = self.getDataRaw().encode("utf-8")

            self.__data = data_time + dataRawEncoded

        def __packAndRecalculateChecksum(self):
            # Checksum is calculated with the following sequence to confirm data in up to date
            self.__packHeader()                 # packHeader() and encodeData() transfer data to their respective bit
                                                # locations, otherwise, the bit sequences are empty or incorrect.
            self.__encodeData()
            self.__recalculateChecksum()        # Result will set new checksum value
            self.__packHeader()                 # Header is rebuilt to include new checksum value

        def __validateIcmpReplyPacketWithOriginalPingData(self, icmpReplyPacket):
            # print("Print contents of reply packet", dir(icmpReplyPacket))       # Printing out values for debugging purposes
            icmpReplyPacket.setIsValidResponse(True)

            print()
            print("DETERMING VALIDITY: ")
            if self.getPacketSequenceNumber() != icmpReplyPacket.getIcmpSequenceNumber():
                # Setting validity of overall response/values
                icmpReplyPacket.setIsValidResponse(False)
                icmpReplyPacket.setSequenceNumberValid(False)
            
            # Debug Messages
            print("Sequence Number - sent: ", self.getPacketSequenceNumber())
            print("Sequence Number - recieved: ", icmpReplyPacket.getIcmpSequenceNumber())
            print("Is Sequence Number Equal: ", icmpReplyPacket.getSequenceNumberValid())

            
            if self.getPacketIdentifier() != icmpReplyPacket.getIcmpIdentifier():
                # Setting validity of overall response/values
                icmpReplyPacket.setIsValidResponse(False)
                icmpReplyPacket.setPacketIdentifierValid(False)
            
            # Debug Messages
            print("Packet Identifier - sent: ", self.getPacketIdentifier())
            print("Packet Identifier - recieved: ", icmpReplyPacket.getIcmpIdentifier())
            print("Is Packet Identifier Equal: ", icmpReplyPacket.getPacketIdentifierValid())

            if self.getDataRaw() != icmpReplyPacket.getIcmpData():
                # Setting validity of overall response/values
                icmpReplyPacket.setIsValidResponse(False)
                icmpReplyPacket.setRawDataValid(False)
            
            # Debug Messages
            print("Raw Data - sent: ", self.getDataRaw())
            print("Raw Data - recieved: ", icmpReplyPacket.getIcmpData())
            print("Is Raw Data Equal: ", icmpReplyPacket.getRawDataValid())
            
            print()

        # IcmpPacket Class Public Functions                                                                            
        def buildPacket_echoRequest(self, packetIdentifier, packetSequenceNumber):
            self.setIcmpType(8)
            self.setIcmpCode(0)
            self.setPacketIdentifier(packetIdentifier)
            self.setPacketSequenceNumber(packetSequenceNumber)
            self.__dataRaw = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            self.__packAndRecalculateChecksum()

        def sendEchoRequest(self):
            global packet_loss
            if len(self.__icmpTarget.strip()) <= 0 | len(self.__destinationIpAddress.strip()) <= 0:
                self.setIcmpTarget("127.0.0.1")

            print("Pinging (" + self.__icmpTarget + ") " + self.__destinationIpAddress)

            mySocket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
            mySocket.settimeout(self.__ipTimeout)
            mySocket.bind(("", 0))
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', self.getTtl()))  # Unsigned int - 4 bytes
            try:
                mySocket.sendto(b''.join([self.__header, self.__data]), (self.__destinationIpAddress, 0))
                timeLeft = 30
                pingStartTime = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                endSelect = time.time()
                howLongInSelect = (endSelect - startedSelect)
                if whatReady[0] == []:  # Timeout
                    print("  *        *        *        *        *    Request timed out.")
                recvPacket, addr = mySocket.recvfrom(1024)  # recvPacket - bytes object representing data received
                # addr  - address of socket sending data
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    print("  *        *        *        *        *    Request timed out (By no remaining time left).")

                else:
                    # Fetch the ICMP type and code from the received packet
                    icmpType, icmpCode = recvPacket[20:22]

                    if icmpType == 11:                          # Time Exceeded
                        packet_loss = packet_loss + 1
                        print("ERROR 11: Time Exceeded")
                        print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    %s" %
                                (
                                    self.getTtl(),
                                    (timeReceived - pingStartTime) * 1000,
                                    icmpType,
                                    icmpCode,
                                    addr[0]
                                )
                              )

                    elif icmpType == 3:                         # Destination Unreachable
                        packet_loss = packet_loss + 1
                        print("ERROR 3: Destination Network Unreachable")

                        # printing errors if destination network unreachable
                        if icmpCode == 0:
                            print("Code 0: net unreachable")
                        elif icmpCode == 1:
                            print("Code 1: host unreachable")
                        elif icmpCode == 2:
                            print("Code 2: protocol unreachable")
                        elif icmpCode == 3:
                            print("Code 3: port unrecahable")
                        elif icmpCode == 4:
                            print("Code 4: fragmentation needed")
                        elif icmpCode == 5:
                            print("Code 5: source root failed")
                        elif icmpCode == 6:
                            print("Code 6: destination network unknown")
                        elif icmpCode == 7:
                            print("Code 7: destination host unknown")
                        elif icmpCode == 8:
                            print("Code 8: source host isolated")

                        print("  TTL=%d    RTT=%.0f ms    Type=%d    Code=%d    %s" %
                                  (
                                      self.getTtl(),
                                      (timeReceived - pingStartTime) * 1000,
                                      icmpType,
                                      icmpCode,
                                      addr[0]
                                  )
                              )

                    elif icmpType == 0:                         # Echo Reply
                        icmpReplyPacket = IcmpHelperLibrary.IcmpPacket_EchoReply(recvPacket)
                        self.__validateIcmpReplyPacketWithOriginalPingData(icmpReplyPacket)
                        icmpReplyPacket.printResultToConsole(self.getTtl(), timeReceived, addr, self)
                        return      # Echo reply is the end and therefore should return

                    else:
                        print("error")
            except timeout:
                print("  *        *        *        *        *    Request timed out (By Exception).")
            finally:
                mySocket.close()

        def printIcmpPacketHeader_hex(self):
            print("Header Size: ", len(self.__header))
            for i in range(len(self.__header)):
                print("i=", i, " --> ", self.__header[i:i+1].hex())

        def printIcmpPacketData_hex(self):
            print("Data Size: ", len(self.__data))
            for i in range(len(self.__data)):
                print("i=", i, " --> ", self.__data[i:i + 1].hex())

        def printIcmpPacket_hex(self):
            print("Printing packet in hex...")
            self.printIcmpPacketHeader_hex()
            self.printIcmpPacketData_hex()

    # Class IcmpPacket_EchoReply                                                                                      
    class IcmpPacket_EchoReply:
        # IcmpPacket_EchoReply Class Scope Variables                                                                  
        __recvPacket = b''
        __isValidResponse = False
        __SequenceNumberValid = True
        __PacketIdentifierValid = True
        __RawDataValid = True

        # IcmpPacket_EchoReply Constructors                                                                           
        def __init__(self, recvPacket):
            self.__recvPacket = recvPacket

        # IcmpPacket_EchoReply Getters                                                                                
        def getIcmpType(self):
            # Method 1
            # bytes = struct.calcsize("B")        # Format code B is 1 byte
            # return struct.unpack("!B", self.__recvPacket[20:20 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("B", 20)

        def getIcmpCode(self):
            # Method 1
            # bytes = struct.calcsize("B")        # Format code B is 1 byte
            # return struct.unpack("!B", self.__recvPacket[21:21 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("B", 21)

        def getIcmpHeaderChecksum(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[22:22 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 22)

        def getIcmpIdentifier(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[24:24 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 24)

        def getIcmpSequenceNumber(self):
            # Method 1
            # bytes = struct.calcsize("H")        # Format code H is 2 bytes
            # return struct.unpack("!H", self.__recvPacket[26:26 + bytes])[0]

            # Method 2
            return self.__unpackByFormatAndPosition("H", 26)

        def getDateTimeSent(self):
            # This accounts for bytes 28 through 35 = 64 bits
            return self.__unpackByFormatAndPosition("d", 28)   # Used to track overall round trip time
                                                               # time.time() creates a 64 bit value of 8 bytes
        def getIcmpData(self):
            # This accounts for bytes 36 to the end of the packet.
            return self.__recvPacket[36:].decode('utf-8')

        def isValidResponse(self):
            return self.__isValidResponse
        
        def getSequenceNumberValid(self):
            return self.__SequenceNumberValid
        
        def getPacketIdentifierValid(self):
            return self.__PacketIdentifierValid
        
        def getRawDataValid(self):
            return self.__RawDataValid

        # IcmpPacket_EchoReply Setters                                                                                 #
        def setIsValidResponse(self, booleanValue):
            self.__isValidResponse = booleanValue

        def setSequenceNumberValid(self, booleanValue):
            self.__SequenceNumberValid = booleanValue
        
        def setPacketIdentifierValid(self, booleanValue):
            self.__PacketIdentifierValid = booleanValue
        
        def setRawDataValid(self, booleanValue):
            self.__RawDataValid = booleanValue

        # IcmpPacket_EchoReply Private Functions                                                                       #
        def __unpackByFormatAndPosition(self, formatCode, basePosition):
            numberOfbytes = struct.calcsize(formatCode)
            return struct.unpack("!" + formatCode, self.__recvPacket[basePosition:basePosition + numberOfbytes])[0]

        # IcmpPacket_EchoReply Public Functions                                                                        #
        def printResultToConsole(self, ttl, timeReceived, addr, actual):
            bytes = struct.calcsize("d")
            timeSent = struct.unpack("d", self.__recvPacket[28:28 + bytes])[0]
            global total_RTT
            global min_RTT
            global max_RTT
            global total_data
            global packet_loss
            

            # Printing message based on echo's validity
            if self.isValidResponse():
                total_data = total_data + sys.getsizeof(actual.getDataRaw())
                print("VALID RESPONSE: ")
            else:
                # calcuating packet loss
                packet_loss = packet_loss + 1
                print()
                print("INVALID RESPONSE: ")
                print("Expected Values:   Identifier=%d    Sequence Number=%d   Raw Data=%s" %
                    (
                        actual.getPacketIdentifier(),
                        actual.getPacketSequenceNumber(),
                        actual.getDataRaw(),
                    )
                    )

            print("Recieved Values:   TTL=%d    RTT=%.0f ms    Type=%d    Code=%d     Identifier=%d    Sequence Number=%d   Raw Data=%s    %s" %
                  (
                      ttl,
                      (timeReceived - timeSent) * 1000,
                      self.getIcmpType(),
                      self.getIcmpCode(),
                      self.getIcmpIdentifier(),
                      self.getIcmpSequenceNumber(),
                      self.getIcmpData(),
                      addr[0]
                  )
                 )

            # Updating Metrics
            RTT = float(timeReceived - timeSent) * 1000,
            RTT = RTT[0]
            total_RTT = total_RTT + RTT
            if RTT < min_RTT:
                min_RTT = RTT
            if RTT > max_RTT:
                max_RTT = RTT

            # printing a line between each ping
            print()
            print("______________________________________________________________________________________________________________________________________________________________________________________")
            print()

    # Class IcmpHelperLibrary                                                                                          
    # IcmpHelperLibrary Class Scope Variables                                                                          
    __DEBUG_IcmpHelperLibrary = False                  # Allows for debug output

    # IcmpHelperLibrary Private Functions                                                                              
    def __sendIcmpEchoRequest(self, host):
        print("sendIcmpEchoRequest Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        global packets_sent
        packets_sent = 10

        for i in range(packets_sent):
            # Build packet
            icmpPacket = IcmpHelperLibrary.IcmpPacket()

            randomIdentifier = (os.getpid() & 0xffff)      # Get as 16 bit number - Limit based on ICMP header standards
                                                           # Some PIDs are larger than 16 bit

            packetIdentifier = randomIdentifier
            packetSequenceNumber = i

            icmpPacket.buildPacket_echoRequest(packetIdentifier, packetSequenceNumber)  # Build ICMP for IP payload
            icmpPacket.setIcmpTarget(host)
            icmpPacket.sendEchoRequest()                                                # Build IP

            icmpPacket.printIcmpPacketHeader_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            icmpPacket.printIcmpPacket_hex() if self.__DEBUG_IcmpHelperLibrary else 0

    def __sendIcmpTraceRoute(self, host):
        print("sendIcmpTraceRoute Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        global packets_sent
        packets_sent = 200      # this represents the max TTL number 

        for i in range(packets_sent):
            # Build packet
            icmpPacket = IcmpHelperLibrary.IcmpPacket()
            icmpPacket.setTtl(i)

            randomIdentifier = (os.getpid() & 0xffff)      # Get as 16 bit number - Limit based on ICMP header standards
                                                           # Some PIDs are larger than 16 bit

            packetIdentifier = randomIdentifier
            packetSequenceNumber = i

            icmpPacket.buildPacket_echoRequest(packetIdentifier, packetSequenceNumber)  # Build ICMP for IP payload
            icmpPacket.setIcmpTarget(host)
            icmpPacket.sendEchoRequest()                                                # Build IP

            icmpPacket.printIcmpPacketHeader_hex() if self.__DEBUG_IcmpHelperLibrary else 0
            icmpPacket.printIcmpPacket_hex() if self.__DEBUG_IcmpHelperLibrary else 0

    def sendPing(self, targetHost):
        print("ping Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        self.__sendIcmpEchoRequest(targetHost)

    def traceRoute(self, targetHost):
        print("traceRoute Started...") if self.__DEBUG_IcmpHelperLibrary else 0
        self.__sendIcmpTraceRoute(targetHost)

def main():
    icmpHelperPing = IcmpHelperLibrary()
    # Choose one of the following by uncommenting out the line
    # icmpHelperPing.sendPing("209.233.126.254")
    # icmpHelperPing.sendPing("www.google.com")
    # icmpHelperPing.sendPing("oregonstate.edu")
    # icmpHelperPing.sendPing("gaia.cs.umass.edu")
    # icmpHelperPing.traceRoute("oregonstate.edu")
    # icmpHelperPing.traceRoute("www.google.com")
    # icmpHelperPing.traceRoute("www.amazon.com")
    # icmpHelperPing.traceRoute("www.olx.in")
    icmpHelperPing.traceRoute("www.naver.com")

    print("PING METRICS")
    print("average RTT: ", total_RTT / packets_sent)
    print("min RTT: ", min_RTT)
    print("max RTT: ", max_RTT)
    print("packet loss: ", (packet_loss / packets_sent) * 100, "%")
    print("packets lost: ", packet_loss)
    print("total data sent: ", total_data, " bytes")

if __name__ == "__main__":
    main()