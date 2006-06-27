#!/usr/bin/env python

# Code to parse the different table types in a DVB transport stream

from CRC import dvbcrc

from Axon.Component import component
from Axon.Ipc import producerFinished,shutdownMicroprocess
from Descriptors import parseDescriptor

def ParseSDT_ActualNetwork():
    return ParseSDT(accept_tableID = 0x42)

def ParseSDT_OtherNetwork():
    return ParseSDT(accept_tableID = 0x46)

_running_status = [
        0,
        "NOT RUNNING",
        "STARTS SOON",
        "PAUSING",
        "RUNNING",
        5,
        6,
        7,
    ]

class ParseSDT(component):
    """
    Parses a SDT table.
    
    Receives table sections from PSI packets. Once all sections have been
    gathered; parses the table and outputs a dictionary containing the contents.
    
    Doesn't emit anything again until the version number of the table changes.
    
    Outputs both 'current' and 'next' tables.
    
    Can only handle one SDT at a time ... you can't feed it mutiple SDTs from
    multiple PIDs. Nor will it handle more than one table id simultaneously.
    """
    Inboxes = { "inbox" : "DVB PSI Packets from a single PID containing SDT table sections",
                "control" : "Shutdown signalling",
              }
    Outboxes = { "outbox" : "Parsed PMT table (only when it changes)",
                 "signal" : "Shutdown signalling",
               }
               
    def __init__(self, accept_tableID = 0x42):
        super(ParseSDT,self).__init__()
        self.tid = accept_tableID

    def parseTable(self, table_id, current_next, sections):
        
        msg = { "table_type"          : "SDT",
                "table_id"            : table_id,
                "current"             : current_next,
              }
        services = {}
        
        for (data,section_length) in sections:
            
            msg["transport_stream_id"] = (ord(data[3])<<8) + ord(data[4])
            msg["orginal_network_id"]  = (ord(data[8])<<8) + ord(data[9])
            
            i=11
            while i < section_length+3-4:
                service_id = (ord(data[i])<<8) + ord(data[i+1])
                service = {}
                
                lo = ord(data[i+2])
                service['eit_schedule']          = lo & 0x02
                service['eit_present_following'] = lo & 0x01
                hi = ord(data[i+3])
                service['running_status']        = hi >> 5
                service['scrambled']             = hi & 0x10
                
                descriptors_length = ((hi<<8) + ord(data[i+4])) & 0x0fff
                i = i + 5
                descriptors_end = i + descriptors_length
                service['descriptors'] = []
                while i < descriptors_end:
                    descriptor,i = parseDescriptor(i,data)
                    service['descriptors'].append(descriptor)
                    
                services[service_id] = service
            
        msg['services'] = services
        
        return  msg
    
    def shutdown(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            self.send(msg,"signal")
            if isinstance(msg, (shutdownMicroprocess, producerFinished)):
                return True
        return False
    
    def main(self):
        # initialise buffers
        # ...for holding table sections (until we get  complete table)
        
        # indexed by (current_next, transport_stream_id, original_network_id)
        sections = {}
        latest_versions = {}
        last_section_numbers = {}
        missing_sections_count = {}
        
        while not self.shutdown():
             
            while self.dataReady("inbox"):
                data = self.recv("inbox")
                
                # extract basic info from this PSI packet - enough to work
                # out what table it is; what section, and the version
                e = [ord(data[i]) for i in (0,1,2,3,4,5,6,7,8,9) ]

                table_id = e[0]
                if table_id != self.tid:
                    continue
                
                syntax = e[1] & 0x80
                if not syntax:
                    continue
                
                section_length = ((e[1]<<8) + e[2]) & 0x0fff
                
                version = (e[5] &0x3e)  # no need to >> 1
                current_next = e[5] & 0x01
                section_number = e[6]
                last_section_number = e[7]

                transport_stream_id = (e[3]<<8) + e[4]
                original_network_id  = (e[8]<<8) + e[9]
                
                index = (current_next, transport_stream_id, original_network_id)

                # if version number has changed, flush out all previously fetched tables
                crcpass = False
                if version != latest_versions.get(index,-1):
                    if not dvbcrc(data[:3+section_length]):
                        continue
                    else:
                        crcpass = True
                    latest_versions[index] = version
                    
                    sections[index] = [None]*(last_section_number+1)
                    missing_sections_count[index] = last_section_number+1
                
                if sections[index][section_number] == None:
                    if crcpass or dvbcrc(data[:3+section_length]):
                        
                        sections[index][section_number] = (data, section_length)
                        missing_sections_count[index] -= 1
                        
                        # see if we have all sections of the table
                        # if we do, send the whole bundle onwards
                        if missing_sections_count[index] == 0:
                            table = self.parseTable(table_id, current_next, sections[index])
                            self.send( table, "outbox")
                        
            self.pause()
            yield 1


class SDT_to_SimpleServiceList(component):
    
    def shutdown(self):
        while self.dataReady("control"):
            msg = self.recv("control")
            self.send(msg,"signal")
            if isinstance(msg, (shutdownMicroprocess, producerFinished)):
                return True
        return False
    
    def main(self):
        while not self.shutdown():
            while self.dataReady("inbox"):
                sdt = self.recv("inbox")
                s =dict([(service['descriptors'][0][1]['service_name'],sid) for (sid,service) in sdt['services'].items()])
                self.send(s,"outbox")
            self.pause()
            yield 1


if __name__ == "__main__":
    
    from Kamaelia.Util.PipelineComponent import pipeline
    from Kamaelia.Device.DVB.Core import DVB_Multiplex, DVB_Demuxer
    from Kamaelia.Device.DVB.EIT import PSIPacketReconstructor
    from Kamaelia.Util.Console import ConsoleEchoer
    from Kamaelia.Util.Fanout import fanout
    from Kamaelia.Util.Graphline import Graphline
    
    import dvb3.frontend
    feparams = {
        "inversion" : dvb3.frontend.INVERSION_AUTO,
        "constellation" : dvb3.frontend.QAM_16,
        "coderate_HP" : dvb3.frontend.FEC_3_4,
        "coderate_LP" : dvb3.frontend.FEC_3_4,
    }
    
    SDTPARSE = Graphline( ACTUAL = ParseSDT_ActualNetwork(),
                          OTHER  = ParseSDT_OtherNetwork(),
                          FANOUT = fanout(["other"]),
                          linkages = { ("self","inbox") : ("FANOUT","inbox"),
                                       ("FANOUT","outbox") : ("ACTUAL","inbox"),
                                       ("FANOUT","other")  : ("OTHER","inbox"),
                                       ("ACTUAL","outbox") : ("self","outbox"),
                                       ("OTHER","outbox") : ("self","outbox"),
                                     }
                        )

    pipeline( DVB_Multiplex(505833330.0/1000000.0, [0x11], feparams),
              DVB_Demuxer({ 0x11:["outbox"]}),
              PSIPacketReconstructor(),
              SDTPARSE,
              SDT_to_SimpleServiceList(),
              ConsoleEchoer(),
            ).run()

