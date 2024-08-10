# if self.getPacketSequenceNumber() != icmpReplyPacket.getIcmpSequenceNumber():
#                 # Debug Messages
#                 print("ERROR: Sequence Number - sent: ", self.getPacketSequenceNumber())
#                 print("ERROR: Sequence Number - recieved: ", icmpReplyPacket.getIcmpSequenceNumber())

#                 # Setting validity of overall response/values
#                 icmpReplyPacket.setIsValidResponse(False)
#                 icmpReplyPacket.setSequenceNumberValid(False)
            
#             if self.getPacketIdentifier() != icmpReplyPacket.getIcmpIdentifier():
#                 # Debug Messages
#                 print("ERROR: Packet Identifier - sent: ", self.getPacketIdentifier())
#                 print("ERROR: Packet Identifier - recieved: ", icmpReplyPacket.getIcmpIdentifier())

#                 # Setting validity of overall response/values
#                 icmpReplyPacket.setIsValidResponse(False)
#                 icmpReplyPacket.setPacketIdentifierValid(False)

#             if self.getDataRaw() != icmpReplyPacket.getIcmpData():
#                 # Debug Messages
#                 print("ERROR: Raw Data - sent: ", self.getDataRaw())
#                 print("ERROR: Raw Data - recieved: ", icmpReplyPacket.getIcmpData())\

                total_data = total_data + sys.getsizeof(actual.getDataRaw())
