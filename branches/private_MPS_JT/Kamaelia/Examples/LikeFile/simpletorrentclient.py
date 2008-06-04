#!/usr/bin/env python

# A demonstration of using likefile to control a torrent downloader.

import Axon.LikeFile, time, sys
from Kamaelia.Protocol.Torrent.TorrentPatron import TorrentPatron
from Kamaelia.Protocol.Torrent.TorrentClient import BasicTorrentExplainer
from Kamaelia.File.TriggeredFileReader import TriggeredFileReader
from Kamaelia.Chassis.Pipeline import Pipeline

Axon.LikeFile.background(slowmo=0.01).start()

try: filename = sys.argv[1]
except IndexError:
    print "usage: ./simpletorrentclient.py <filename.torrent>"
    sys.exit(1)


torrenter = Axon.LikeFile.likefile(
    Pipeline(TriggeredFileReader(),
        TorrentPatron(),
        BasicTorrentExplainer(),
        ))

torrenter.put(filename)
try:
    while True:
        print torrenter.get()
except KeyboardInterrupt:
        torrenter.shutdown()