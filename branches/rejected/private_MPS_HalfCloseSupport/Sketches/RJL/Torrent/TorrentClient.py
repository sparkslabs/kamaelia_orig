#!/usr/bin/env python

# The contents of this file are subject to the BitTorrent Open Source License
# Version 1.1 (the License).  You may not copy or use this file, in either
# source code or executable form, except in compliance with the License.  You
# may obtain a copy of the License at http://www.bittorrent.com/license/.
#
# Software distributed under the License is distributed on an AS IS basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied.  See the License
# for the specific language governing rights and limitations under the
# License.

# Written by Bram Cohen, Uoti Urpala, John Hoffman, and David Harrison

from __future__ import division

from BitTorrent.translation import _

import pdb
import sys
import os
from cStringIO import StringIO
import logging
from logging import ERROR
from time import strftime, sleep
import traceback

import BitTorrent.stackthreading as threading
from BitTorrent.defer import DeferredEvent
from BitTorrent import inject_main_logfile
from BitTorrent.MultiTorrent import Feedback, MultiTorrent
from BitTorrent.defaultargs import get_defaults
from BitTorrent.parseargs import printHelp
from BitTorrent.zurllib import urlopen
from BitTorrent.prefs import Preferences
from BitTorrent import configfile
from BitTorrent import BTFailure
from BitTorrent import version
from BitTorrent import console, stderr_console
from BitTorrent import GetTorrent
from BitTorrent.RawServer_twisted import RawServer, task
from BitTorrent.ConvertedMetainfo import ConvertedMetainfo
from BitTorrent.platform import get_temp_dir
inject_main_logfile()

from Axon.Ipc import shutdown, producerFinished
from Axon.ThreadedComponent import threadedcomponent
from Axon.Component import component

from TorrentIPC import *

"""\
=================
TorrentClient - a BitTorrent Client
=================

This component is for downloading and uploading data using the peer-to-peer
BitTorrent protocol.

I should start by saying "DO NOT USE THIS COMPONENT YOURSELF".

This component wraps the Mainline (official) BitTorrent client, which
unfortunately is not thread-safe (at least with the latest version - 4.20).
If you run two instances of this client simultaneously, Python will die
with an exception, or if you're really unlucky, a segfault.

But despair not! There is a solution - use TorrentHandler instead.
TorrentHandlers will organise the sharing of a single TorrentClient amongst
themselves and expose exactly the same interface (except that the
tickInterval optional argument cannot be set) with the key advantage
that you can run as many of them as you want.

For a description of the interfaces of TorrentClient see TorrentHandler.py.

How does it work?
-----------------

TorrentClient is a threadedcomponent that uses the libraries of the Mainline
(official) BitTorrent client to provide BitTorrent functionality. As Mainline
was designed to block (use blocking function calls) this makes it incompatible
with the normal structure of an Axon component - it cannot yield regularly.
As such it uses a threadedcomponent, allowing it to block with impunity.

Each torrent is assigned a unique id (currently equal to the count of torrents
seen but don't rely on it). Inboxes are checked periodically (every tickInterval
seconds, where tickInterval is 5 by default)

TorrentClient currently cannot be shutdown.
"""

class MakeshiftTorrent(object):
    """While a torrent is started, an instance of this class is used in place of
    a real Torrent object (a class from Mainline) to store its metainfo"""
    
    def __init__(self, metainfo):
        super(MakeshiftTorrent, self).__init__()
        self.metainfo = metainfo
        
class TorrentClient(threadedcomponent):
    """\
    TorrentClient([tickInterval]) -> component capable of downloading/sharing torrents.

    Initialises the Mainline client.
   
    Arguments:
    - [tickInterval=5] -- the interval in seconds at which TorrentClient checks inboxes
    
    Using threadedcomponent so we don't have to worry about blocking I/O or making
    mainline yield periodically
    """
    
    Inboxes = {
        "inbox"   : "Torrent IPC - add a torrent, stop a torrent etc.",
        "control" : "NOT USED"
    }
    Outboxes = {
        "outbox"  : "Torrent IPC - status updates, completion, new torrent added etc.",
        "signal"  : "NOT USED"
    }

    def __init__(self, tickInterval = 5):
        super(TorrentClient, self).__init__()
        self.totaltorrents = 0
        self.torrents = {}
        self.torrentinfohashes = {}
        self.tickInterval = tickInterval #seconds
        
    def main(self):
        """\
        Start the Mainline client and block forever listening for connectons
        """
      
        uiname = "bittorrent-console"
        defaults = get_defaults(uiname)
        config, args = configfile.parse_configuration_and_args(defaults, uiname)
        config = Preferences().initWithDict(config)
        data_dir = config['data_dir']
        self.core_doneflag = DeferredEvent()
        self.rawserver_doneflag = DeferredEvent()
        
        rawserver = RawServer(config) #event and I/O scheduler
        self.multitorrent = MultiTorrent(config, rawserver, data_dir) #class used to add, control and remove torrents

        self.tick() #add periodic function call
    
        rawserver.add_task(0, self.core_doneflag.addCallback, lambda r: rawserver.external_add_task(0, shutdown))
        rawserver.listen_forever(self.rawserver_doneflag)

        self.send(producerFinished(self), "signal")
        print "TorrentClient has shutdown"
                        
    def startTorrent(self, metainfo, save_incomplete_as, save_as, torrentid):
        """startTorrent causes MultiTorrent to begin downloading a torrent eventually.
        Use it instead of _start_torrent."""
        
        self._create_torrent(metainfo, save_incomplete_as, save_as)
        self.multitorrent.rawserver.add_task(1, self._start_torrent, metainfo, torrentid)
            
    def _create_torrent(self, metainfo, save_incomplete_as, save_as):
        if not self.multitorrent.torrent_known(metainfo.infohash):
            df = self.multitorrent.create_torrent(metainfo, save_incomplete_as, save_as)                
        #except Exception, e:
        #    print e
        #    return False
                
    def _start_torrent(self, metainfo, torrentid):
        #try:
        t = None
        if self.multitorrent.torrent_known( metainfo.infohash ):
            t = self.multitorrent.get_torrent(metainfo.infohash)
    
        # HACK!! Rewrite when INITIALIZING state is available.
        if t is None or not t.is_initialized():
            #self.logger.debug( "Waiting for torrent to initialize." )
            self.multitorrent.rawserver.add_task(3, self._start_torrent, metainfo, torrentid)
            return

        if not self.multitorrent.torrent_running(metainfo.infohash):
            df = self.multitorrent.start_torrent(metainfo.infohash)
            self.torrents[torrentid] = self.multitorrent.get_torrent(metainfo.infohash)
            
            #yield df
            #df.getResult()  # raises exception if one occurred in yield.
        
        #    print e
        #    print "Failed to start torrent"

    def decodeTorrent(self, data):
        """\
        Converts bencoded raw metadata (as one would find in a .torrent file) into
        a metainfo object (which one can then get the torrent's properties from).
        """
            
        from BitTorrent.bencode import bdecode, bencode
        metainfo = None
        try:
            b = bdecode(data)
            metainfo = ConvertedMetainfo(b)
        except Exception, e:
            pass
        return metainfo
        
    def tick(self):
        """\
        Called periodically... by itself (gets rawserver to call it back after a delay of
        tickInterval seconds). Checks inboxes and sends a status-update message for every
        active torrent.
        """

        self.multitorrent.rawserver.add_task(self.tickInterval, self.tick)
        #print "Tick"
        while self.dataReady("inbox"):
            temp = self.recv("inbox")
            if isinstance(temp, TIPCCreateNewTorrent) or isinstance(temp, str):
                if isinstance(temp, str):
                    metainfo = self.decodeTorrent(temp)
                else:
                    metainfo = self.decodeTorrent(temp.rawmetainfo)
                if metainfo != None:
                    savefolder = os.path.join("./",metainfo.name_fs)
                    
                    existingTorrentId = self.torrentinfohashes.get(metainfo.infohash, 0)
                    if existingTorrentId != 0:
                        self.send(TIPCTorrentAlreadyDownloading(torrentid=existingTorrentId), "outbox")
                    else:
                        self.totaltorrents += 1
                        self.torrentinfohashes[metainfo.infohash] = self.totaltorrents
                        self.torrents[self.totaltorrents] = MakeshiftTorrent(metainfo)                    
                        self.startTorrent(metainfo, savefolder, savefolder, self.totaltorrents)
                        self.send(TIPCNewTorrentCreated(torrentid=self.totaltorrents, savefolder=savefolder), "outbox")
            elif isinstance(temp, TIPCCloseTorrent):
                torrent = self.torrents.get(temp.torrentid, None)
                if torrent != None:
                    self.multitorrent.remove_torrent(torrent.metainfo.infohash)
                    self.torrentinfohashes.erase(torrent.metainfo.infohash)
                    self.torrents.erase(temp.torrentid)
                    
        for torrentid, torrent in self.torrents.items():
            if not isinstance(torrent, MakeshiftTorrent):
                self.send(TIPCTorrentStatusUpdate(torrentid=torrentid, statsdictionary=torrent.get_status()), "outbox")
        
        while self.dataReady("control"):
            temp = self.recv("control")
            if isinstance(temp, shutdown):
                print "TorrentClient trying to shutdown"
                #cause us to shutdown
                self.rawserver_doneflag.set()
                self.core_doneflag.set()
        #if self.torrent is not None:
        #    status = self.torrent.get_status(self.config['spew'])
        #    self.d.display(status)


class BasicTorrentExplainer(component):
    """\
    BasicTorrentExplainer() -> component useful for debugging TorrentClient/TorrentPatron

    This component converts each torrent IPC messags it receives into human readable
    line of text.
    """
    def main(self):
        while 1:
            yield 1
            while self.dataReady("inbox"):
                temp = self.recv("inbox")
                #try:
                self.send(temp.getText() + "\n", "outbox")
                #except:
                #    pass
            self.pause()
           
if __name__ == '__main__':
    from Kamaelia.Util.PipelineComponent import pipeline
    from Kamaelia.Util.Console import ConsoleReader, ConsoleEchoer
    
    import sys
    sys.path.append("../Util/")
    
    from TriggeredFileReader import TriggeredFileReader
    from Axon.Component import component

    # download a linux distro or whatever
    # NOTE: Do not follow this example. It is used to illustrate/test the use of a TorrentClient component
    # alone. TorrentPatron can and should be used in place of TorrentClient for user applications
    # as it supports multiple instances (create two TorrentClients and see it all come falling down).
    pipeline(
        ConsoleReader(">>> ", ""),
        TriggeredFileReader(),
        TorrentClient(),
        BasicTorrentExplainer(),
        ConsoleEchoer(),    
    ).run()   

            
