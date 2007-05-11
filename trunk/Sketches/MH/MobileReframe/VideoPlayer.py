#!/usr/bin/env python

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
#

import sys
if len(sys.argv)!=2:
    sys.stderr.write("Usage:\n\n    "+sys.argv[0]+" <videofile>\n\n")
    sys.exit(1)
else:
    infile=sys.argv[1]
    infile=infile.replace(" ","\ ")

    


from Kamaelia.Util.Detuple import SimpleDetupler

from Kamaelia.Codec.YUV4MPEG import YUV4MPEGToFrame
from Kamaelia.UI.Pygame.VideoOverlay import VideoOverlay
from Kamaelia.Audio.PyMedia.Output import Output
#from Output import Output

import sys
from UnixProcess import UnixProcess
from Chassis import Pipeline,Graphline,Carousel
from InboxControlledCarousel import InboxControlledCarousel
from StopSelector import StopSelector

#from Kamaelia.Util.RateFilter import MessageRateLimit
from Kamaelia.Util.RateFilter import ByteRate_RequestControl
#from ByteRate_RequestControl import ByteRate_RequestControl
from Kamaelia.Util.Detuple import SimpleDetupler
from Kamaelia.Util.TwoWaySplitter import TwoWaySplitter
from Kamaelia.Util.FirstOnly import FirstOnly
from Kamaelia.Util.PureTransformer import PureTransformer
#from Kamaelia.Util.PromptedTurnstile import PromptedTurnstile
from PromptedTurnstile import PromptedTurnstile
from Kamaelia.Codec.WAV import WAVParser

from Kamaelia.Util.Console import ConsoleEchoer

from Kamaelia.UI.Pygame.Display import PygameDisplay

from Kamaelia.Video.PixFormatConversion import ToRGB_interleaved
from Kamaelia.UI.Pygame.VideoSurface import VideoSurface

import pygame

sys.path.append("../Introspection")
from Profiling import Profiler
Profiler().activate()

def FrameRateLimitedPlayback(player):
    def RateLimitedPlayback(frame):
        fps = frame["frame_rate"]
        x,y = tuple(frame["size"])
        print "Frames per second:",fps
        print "(width,height):",(x,y)
        
        pgd = PygameDisplay(width=x,height=y).activate()
        PygameDisplay.setDisplayService(pgd)

        return Graphline( \
            LIMIT = PromptedTurnstile(),
            RATE  = ByteRate_RequestControl(rate=fps, chunksize=1.0, allowchunkaggregation=False),
            PLAY  = player,
            linkages = {
                ("",      "inbox" ) : ("LIMIT", "inbox"),
                ("LIMIT", "outbox") : ("PLAY",  "inbox"),
                ("PLAY",  "outbox") : ("",      "outbox"),
                
                ("RATE", "outbox" ) : ("LIMIT", "next"),

                ("",      "control") : ("RATE",  "control"),
                ("RATE",  "signal" ) : ("LIMIT", "control"),
                ("LIMIT", "signal" ) : ("PLAY",  "control"),
                ("PLAY",  "signal" ) : ("",      "signal"),
            },
            boxsizes = {
                ("LIMIT","inbox") : 2,
            },
        )

    return Graphline(\
        SPLIT = TwoWaySplitter(),
        FIRST = FirstOnly(),
        PLAY  = Carousel(RateLimitedPlayback),
        linkages = {
            ("",      "inbox"  ) : ("SPLIT", "inbox"),
            ("SPLIT", "outbox" ) : ("FIRST", "inbox"),
            ("FIRST", "outbox" ) : ("PLAY",  "next"),
            
            ("SPLIT", "outbox2") : ("PLAY",  "inbox"),
            ("PLAY",  "outbox" ) : ("",      "outbox"),
        
            ("",      "control") : ("SPLIT", "control"),
            ("SPLIT", "signal" ) : ("FIRST", "control"),
            ("SPLIT", "signal2") : ("PLAY",  "control"),
            ("PLAY",  "signal" ) : ("",      "signal"),
        },
        boxsizes = {
            ("SPLIT","inbox") : 1,
        },
    )

Graphline( DECODE = UnixProcess(
               "ffmpeg -i "+infile+" -f yuv4mpegpipe -y vidpipe.yuv -f wav -y audpipe.wav",
               outpipes={"vidpipe.yuv":"video","audpipe.wav":"audio"},
               buffersize=131072,
               ),
           VIDEO = Pipeline(
               1, YUV4MPEGToFrame(),
               FrameRateLimitedPlayback(VideoOverlay()),
               ),
           AUDIO = Graphline(
               PARSE = WAVParser(),
               OUT   = Carousel(lambda format :
                   Output(format['sample_rate'],format['channels'],format['sample_format'],maximumLag=0.5)),
               linkages = {
                   ("","inbox")         : ("PARSE","inbox"),
                   ("PARSE","outbox")   : ("OUT","inbox"),
                   ("PARSE","all_meta") : ("OUT","next"),
                          
                   ("","control")     : ("PARSE","control"),
                   ("PARSE","signal") : ("OUT","control"),
                   ("OUT", "signal")  : ("","signal"),
               },
               boxsizes = { ("PARSE","inbox") : 5, },
               ),
           DEBUG = ConsoleEchoer(),
           linkages = {
               ("DECODE", "video") : ("VIDEO", "inbox"),
               ("DECODE", "audio") : ("AUDIO", "inbox"),
               ("DECODE", "outbox") : ("DEBUG", "inbox"),
#               ("DECODE", "error") : ("DEBUG", "inbox"),
                       
               ("DECODE", "signal") : ("AUDIO", "control"),
               ("AUDIO", "signal") : ("VIDEO", "control"),
           },
        ).run()
