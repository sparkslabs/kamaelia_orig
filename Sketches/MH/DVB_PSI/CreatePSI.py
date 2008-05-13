#!/usr/bin/env python
# Copyright (C) 2008 British Broadcasting Corporation and Kamaelia Contributors(1)
#     All Rights Reserved.
#
# You may only modify and redistribute this under the terms of any of the
# following licenses(2): Mozilla Public License, V1.1, GNU General
# Public License, V2.0, GNU Lesser General Public License, V2.1
#
# (1) Kamaelia Contributors are listed in the AUTHORS file and at
#     http://kamaelia.sourceforge.net/AUTHORS - please extend this file,
#     not this notice.
# (2) Reproduced in the COPYING file, and at:
#     http://kamaelia.sourceforge.net/COPYING
# Under section 3.5 of the MPL, we are using this text since we deem the MPL
# notice inappropriate for this file. As per MPL/GPL/LGPL removal of this
# notice is prohibited.
#
# Please contact us via: kamaelia-list-owner@lists.sourceforge.net
# to discuss alternative licensing.
# -------------------------------------------------------------------------
"""\
========================
Construct DVB PSI tables
========================

PSI table sections in ... MPEG transport stream packets out

not yet tested ... or kamaelia-ised!


"""
from Kamaelia.Support.DVB.CRC import __dvbcrc as doDvbCRC
from CreateDescriptors import serialiseDescriptors


class SerialiseEITSection(object):
    """\
    EIT PSI section dictionary structure in ... binary PSI table section out
    """
    def __init__(self, sectionPacketiser):
        super(SerialiseEIT,self).__init__()
        self.sectionPacketiser = sectionPacketiser
      
    def serialise(self, section):
        data = []
        
        if section["current"]:
            currentNextFlag=1
        else:
            currentNextFlag=0
        
        data.insert( chr(section["table_id"]) )
        seclen_index = len(data) # note where the section length field will be inserted once we know its value
        data.insert( chr((section["service_id"] >> 8) & 0xff) \
                   + chr((section["service_id"]     ) & 0xff) \
                   + chr(((section["version"] & 0x1f) << 1) + currentNextFlag) \
                   + chr(section["section"]) \
                   + chr(section["last_section"]) \
                   + chr((section["transport_stream_id"] >> 8) & 0xff) \
                   + chr((section["transport_stream_id"]     ) & 0xff) \
                   + chr((section["original_network_id"] >> 8) & 0xff) \
                   + chr((section["original_network_id"]     ) & 0xff) \
                   )
        try:
            data.insert( chr((section["segment_last_section_number")) )
        except KeyError:
            data.insert( chr((section["last_section_number")) )
        try:
            data.insert( chr((section["last_table_id")) )
        except KeyError:
            data.insert( chr((section["table_id")) )
        
        # now do events
        events = []
        for event in section["events"]:
            mjd, utc = createMJDUTC(*event["starttime"])
            dur = createBCDtime(*event["duration"])
            flags = ((event["running_status"] & 0x7) << 5)
            if event["free_CA_mode"]:
                flags += 0x10
            
            events.insert( chr((event["event_id"] >> 8) & 0xff) \
                         + chr((event["event_id"]     ) & 0xff) \
                         + chr((mjd >> 8) & 0xff)  \
                         + chr((mjd     ) & 0xff)  \
                         + chr((utc >> 16) & 0xff) \
                         + chr((utc >> 8 ) & 0xff) \
                         + chr((utc      ) & 0xff) \
                         + chr((dur >> 16) & 0xff) \
                         + chr((dur >> 8 ) & 0xff) \
                         + chr((dur      ) & 0xff) \
                         )
                         
            elen_index = len(events)  # note where flags and descriptor_loop_length will be inserted
            
            # add descriptors
            descriptors = serialiseDescriptors(event["descriptors"]
            events.insert(descriptors)
            descriptors_loop_length = len(descriptors)
            
            # now we know how long the descriptor loop is, we write the event's length
            events.insert(elen_index,
                chr(flags + (descriptors_loop_length >> 8) & 0x0f) \
              + chr(        (descriptors_loop_length >> 8) & 0xff) \
            )

        # add events onto the end of the packet we're building
        data.extend(events)
        
        # calculate total length of section
        sectionLength = reduce(lambda total,nextStr: total+nextStr, data, 0)
        sectionLength -= 1  # doesn't include bytes up to and including the section length field itself (which hasn't been inserted yet)
        sectionLength += 4 # lets not forget the CRC
        
        data[seclen_index] = chr(0x80 + ((sectionLength >> 8) & 0x0f)) + chr(sectionLength & 0xff)
        
        # now we've assembled everything, calc the CRC, then write the CRC value at the end
        data = data.join("")
        crcval = doDvbCRC(data)
        crc = chr((crcval >> 24) & 0xff) \
            + chr((crcval >> 16) & 0xff) \
            + chr((crcval >> 8 ) & 0xff) \
            + chr((crcval      ) & 0xff)
        
        self.sectionPacketiser.packetise(data + crc)




class PacketiseTableSections(object):
    """\
    PSI table sections in ... transport stream packets out
    """
    def __init__(self, tsPacketMaker):
        super(PacketiseTableSections,self).__init__()
        self.tsPacketiser = tsPacketMaker
        self.leftOvers = ""
        self.leftOvers_Threshold = 0   # threshold for carrying over the end of one section into a packet that starts a new one
        
    def packetise(self, section):
        
        payload = []
        startOffset = 0
        
        if len(self.leftOvers) > 0:
            payload.insert(self.leftOvers)
            startOffset = len(self.leftOvers)
            self.leftOvers = ""

        sStart = 0
        bytesLeft = len(section)
        
        # first packet
        chunkLen = min(bytesLeft, 184-1-startOffset)  # -1 for the pointer_field
        payload.insert(section[sStart:sStart+chunkLen)
        print self.tsPacketiser.packetise(payload.join(""), True, chr(0xff))
        sStart+=chunkLen
        bytesLeft-=chunkLen

        while bytesLeft > 0:
          
            if bytesLeft <= self.leftOvers_Threshold:
                self.leftOvers = section[sStart:]
                break

            # subsequent packets
            chunkLen = min(bytesLeft, 184)  # -1 for the pointer_field
            payload.insert(section[sStart:sStart+chunkLen)
            print self.tsPacketiser.packetise(payload.join(""), False, chr(0xff))
            sStart+=chunkLen
            bytesLeft-=chunkLen




class MakeTransportStreamPackets(object):
    """\
    Payloads in ... transport stream packets out
    """
    def __init__(self, pid, scrambling=0, priority=False):
        super(MakeTransportStreamPackets,self).__init__()
        self.pid = pid
        self.scrambling = scrambling
        self.priority = priority
        
        self.continuityCounter = 0
      
      
    def packetise(self, payload, startIndicator=False, stuffingByte=chr(0xff)):
        packet = []
    
        pidAndFlags = self.pid & 0x1fff
        if startIndicator:
            pidAndFlags += 0x4000
        if self.priority:
            pidAndFlags += 0x2000
            
        # default to no adaption field (lower 2 bits of upper nibble = "01")
        ctrlFlags = (self.scrambling & 0x3) << 6 + 0x10 + self.continuityCounter  
        
        self.continuityCounter = (self.continuityCounter + 1) % 16
    
        packet.insert(chr(0x47))           # start byte
        packet.insert(chr((pidAndFlags>>8) & 0xff))
        packet.insert(chr((pidAndFlags   ) & 0xff))
        packet.insert(chr(ctrlFlags))
    
        if (len(payload) > 184):
            raise "Payload too long to fit in TS packet!"
        
        packet.insert(payload)
        
        if (len(payload) < 184):
            numStuffingBytes = 184-len(payload)
            packet.insert(stuffingByte * numStuffingBytes)
        
        return packet.join("")
