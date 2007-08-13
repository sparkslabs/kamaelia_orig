#!/usr/bin/env python
#
# (C) 2006 British Broadcasting Corporation and Kamaelia Contributors(1)
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
# Licensed to the BBC under a Contributor Agreement: RJL

"""\
===================================
TorrentPatron - A BitTorrent Client
===================================

You MUST have the Mainline (official) BitTorrent client installed for any
BitTorrent stuff to work in Kamaelia.

NOTE: This code has only been successfully tested with version 4.20.8. Problems
have been experienced with other more recent versions regarding a missing or
misplaced language translations file. See http://download.bittorrent.com/dl/?M=D
and download the appropriate version 4.20.8 package for for your platform.




Known quirks
------------
  
* Clear out your ~/.bittorrent/ directory if you get errors
  about torrents including files that are part of other torrents.
* Files can only be downloaded to/uploaded from within the current directory

This component is for downloading and uploading data using the peer-to-peer
BitTorrent protocol.

Use this component in preference to TorrentClient.

This component uses a TorrentService component to co-ordinate the sharing
of a single TorrentClient between many TorrentPatrons. This is necessary
as running more than one instance of TorrentClient will fail
(see TorrentClient.py for a full explanation).



How does it work?
-----------------

When TorrentPatron is first run, it will get a TorrentService object -
if one already exists it will pick that, otherwise it will create a new one.
It then registers itself with this service allowing it to receive messages
from it. Messages TorrentPatron receives on its inbox are forwarded to 
TorrentService (in a TIPCServicePassOn wrapper) which in turn forwards them to
TorrentClient. Messages generated by TorrentClient relevant to the torrents
started by this instance of TorrentPatron are forwarded to it by TorrentService.

The result of this is that inboxes/outboxes used and the IPC messages accepted/
produced are identical to TorrentClient.

These IPC messages may be found in TorrentIPC.py

Those used internally:
* TIPCServicePassOn - used to wrap messages from TorrentPatron for TorrentClient
* TIPCServiceAdd - register this TorrentPatron with a TorrentService
* TIPCServiceRemove - deregister this TorrentPatron with a TorrentService

Those used externally (i.e. seen/sent by user components):

- Send to TorrentPatron:
  
  * TIPCCreateNewTorrent - start a new torrent from the contents of a .torrent file
  * TIPCCloseTorrent - stop a running torrent
  
- Sent by TorrentPatron:
  
  * TIPCNewTorrentCreated - a new torrent has been started from your (oldest) TIPCCreateNewTorrent message
  * TIPCTorrentStartFail - the torrent associated with your (oldest) TIPCCreateNewTorrent message could not be started
  * TIPCTorrentAlreadyDownloading - the torrent associated with your (oldest) TIPCCreateNewTorrent message is already downloading
  * TIPCTorrentStatusUpdate - a status object for one of your active torrents
"""

from Axon.Ipc import shutdown, producerFinished
from Axon.Component import component

from Kamaelia.Protocol.Torrent.TorrentService import TorrentService
from Kamaelia.Protocol.Torrent.TorrentIPC import *

class TorrentPatron(component):
    """Inboxes/outboxes and message behaviour identical to TorrentClient but
    thread-safe so you can create many of these."""
    
    Inboxes = {
        "inbox"          : "Commands for the TorrentClient",
        "torrent-inbox"  : "Received feedback from TorrentClient",
        "control"        : "Shut me down"
    }
                 
    Outboxes = {
        "outbox"         : "Forward feedback from TorrentClient out of",
        "torrent-outbox" : "Talk to TorrentClient with",
        "signal"         : "producerFinished sent when I've shutdown"
    }
                 
                
    def main(self):
        """Main loop of TorrentPatron"""
        
        # get a reference to a TorrentService which we use to interact with TorrentClient and the Mainline BitTorrent code
        torrentService, torrentShutdownService, newTorrentService = TorrentService.getTorrentServices(self.tracker)
        if newTorrentService:
            newTorrentService.activate()
            self.addChildren(newTorrentService)

        # link to and register with the TorrentService
        self.link((self, "torrent-outbox"), torrentService)
        self.send(TIPCServiceAdd(replyService=(self, "torrent-inbox")), "torrent-outbox")
        
        loop = True
        while loop:
            #print "TorrentPatron.main loop"
            yield 1
            
            if self.dataReady("inbox"):
                msg = self.recv("inbox")
                msg = TIPCServicePassOn(replyService=(self, "torrent-inbox"), message=msg)
                self.send(msg, "torrent-outbox")
                
            elif self.dataReady("torrent-inbox"):
                msg = self.recv("torrent-inbox")
                self.send(msg, "outbox")
                
            elif self.dataReady("control"):
                msg = self.recv("control")
                if isinstance(msg, shutdown):
                    loop = False
                    
            else:
                self.pause()
            
            
        #unregister with the service
        self.send(TIPCServiceRemove(replyService=(self, "torrent-inbox")), "torrent-outbox")
        self.send(producerFinished(self), "signal")
        
__kamaelia_components__  = ( TorrentPatron, )

if __name__ == '__main__':
    from Kamaelia.Chassis.Pipeline import pipeline
    from Kamaelia.Util.Console import ConsoleReader, ConsoleEchoer

    from Kamaelia.File.TriggeredFileReader import TriggeredFileReader
    from Kamaelia.Protocol.Torrent.TorrentClient import BasicTorrentExplainer
    
    # Download a .torrent file with your web browser then enter its file path
    # to the console to have TorrentPatron download it for you
    pipeline(
        ConsoleReader(">>> ", ""),
        TriggeredFileReader(),
        TorrentPatron(),
        BasicTorrentExplainer(),
        ConsoleEchoer(),    
    ).run()
