#!/usr/bin/env python
#
# (C) 2004 British Broadcasting Corporation and Kamaelia Contributors(1)
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
# Simple test harness for integrating TCP clients and servers in one system, sharing selector components etc.
#
#

from Axon.Scheduler import scheduler as _scheduler
from FortuneCookieProtocol import FortuneCookieProtocol as _FortuneCookieProtocol
from EchoCheckerProtocolComponent import EchoCheckerProtocol
from EchoProtocolComponent import EchoProtocol
from SimpleServerComponent import SimpleServer as _SimpleServer
from TCPClient import TCPClient as _TCPClient
from ConsoleEcho import consoleEchoer as _consoleEchoer
import Axon as _Axon
from oggFilePlayComponent import oggPlayer

from Axon.Component import component, scheduler
class InternetHandlingTest(component):
   def initialiseComponent(self):
      import random
      clientServerTestPort=random.randint(1500,1599)
      server=_SimpleServer(protocol=EchoProtocol, port=clientServerTestPort).activate()
      self.server=server
      self.addChildren(server)

      clientProtocol = EchoCheckerProtocol()
      self.addChildren(clientProtocol)

      for i in xrange(0,10):
         client=_TCPClient("127.0.0.1",clientServerTestPort, chargen=1)
         self.addChildren(client)
         clientProtocol = EchoCheckerProtocol()
         self.addChildren(clientProtocol)
         self.link((client,"outbox"), (clientProtocol,"inbox"))
         self.link((clientProtocol,"outbox"), (client,"inbox"))
      return _Axon.Ipc.newComponent(*(self.children))

   def mainBody(self):
      self.pause()
      try:
         pass
         #print self.server.children[1]
      except IndexError:
         pass
      return 1
if __name__ == '__main__':
   t = InternetHandlingTest().activate()

   _scheduler.run.runThreads(slowmo=0)

