#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2010 British Broadcasting Corporation and Kamaelia Contributors(1)
#
# (1) Kamaelia Contributors are listed in the AUTHORS file and at
#     http://www.kamaelia.org/AUTHORS - please extend this file,
#     not this notice.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -------------------------------------------------------------------------
"""\
=================
TCP Socket Server
=================

A building block for creating a TCP based network server. It accepts incoming
connection requests and sets up a component to handle the socket which it then
passes on.

This component does not handle the instantiation of components to handle an
accepted connection request. Another component is needed that responds to this
component and actually does something with the newly established connection.
If you require a more complete implementation that does this, see
Kamaelia.Internet.SingleServer or Kamaelia.Chassis.ConnectedServer.



Example Usage
-------------

See Kamaelia.Internet.SingleServer or Kamaelia.Chassis.ConnectedServer for examples of how
this component can be used.

The process of using a TCPServer component can be summarised as:
- Create a TCP Server
- Wait for newCSA messages from the TCP Server's "protocolHandlerSignal" outbox
- Send what you like to CSA's, ensure you recieve data from the CSAs
- Send producerFinished to the CSA to shut it down.


How does it work?
-----------------

This component creates a listener socket, bound to the specified port, and
registers itself and the socket with a selectorComponent so it is notified of
incoming connections. The selectorComponent is obtained by calling
selectorComponent.getSelectorService(...) to look it up with the local
Coordinating Assistant Tracker (CAT).

When the it recieves a new connection it performs an accept, and creates
a ConnectedSocketAdapter (CSA) to handle the activity on that connection.

The CSA is passed in a newCSA(self,CSA) message to TCPServer's
"protocolHandlerSignal" outbox.

The CSA is also registered with the selector service by sending it a
newCSA(self,(CSA,sock)) message, to ensure the CSA is notified of incoming data
on its socket.

The client component(s) using the TCPServer should handle the newly created CSA
passed to it in whatever way it sees fit.

If a socketShutdown message is received on the "_feedbackFromCSA" inbox, then a
shutdownCSA(self, CSA) message is sent to TCPServer's "protocolHandlerSignal"
outbox to notify the client component that the connection has closed.

Also, a shutdownCSA(self, (CSA, sock)) message is sent to the selector service
to deregister the CSA from receiving notifications.

This component does not terminate.
"""

import socket, errno, random, Axon
import Kamaelia.IPC as _ki
from Kamaelia.Internet.ConnectedSocketAdapter import ConnectedSocketAdapter

import time
from Kamaelia.Internet.Selector import Selector

from Kamaelia.IPC import newReader, newWriter
from Kamaelia.IPC import removeReader, removeWriter
from Kamaelia.IPC import serverShutdown
from Axon.Ipc import shutdown, shutdownMicroprocess

class TCPServer(Axon.Component.component):
   """\
   TCPServer(listenport) -> TCPServer component listening on the specified port.

   Creates a TCPServer component that accepts all connection requests on the
   specified port.
   """
   
   Inboxes  = {  "_feedbackFromCSA" : "for feedback from ConnectedSocketAdapter (shutdown messages)",
                # "DataReady"     : "status('data ready') messages indicating new connection waiting to be accepted",
                "newconnection" : "We expected to recieve a message here when a new connection is ready",
                "control" : "we expect to recieve serverShutdown messages here",
              }
   Outboxes = { "protocolHandlerSignal" : "For passing on newly created ConnectedSocketAdapter components",
                "signal"                : "NOT USED",
                "_selectorSignal"       : "For registering newly created ConnectedSocketAdapter components with a selector service",
                "_selectorShutdownSignal" : "To deregister our interest with the selector",
              }

   CSA = ConnectedSocketAdapter
   def __init__(self,listenport, socketOptions=None,**argd):
      """x.__init__(...) initializes x; see x.__class__.__doc__ for signature"""
      super(TCPServer, self).__init__(**argd)
      self.listenport = listenport
      self.socketOptions = socketOptions
      self.listener,junk = self.makeTCPServerPort(listenport, maxlisten=5)
      self.socket_handlers = {}

   def makeTCPServerPort(self, suppliedport=None, HOST=None, minrange=2000,maxrange=50000, maxlisten=5):
      """\
      Returns (socket,port) - a bound TCP listener socket and the port number it is listening on.

      If suppliedPort is not specified, then a random port is chosen between
      minrange and maxrange inclusive.

      maxlisten is the max number of pending requests the server will allow (queue up).
      """
      if HOST is None: HOST=''
      if suppliedport is None:
         PORT=random.randint(minrange,maxrange) # Built in support for testing
      else:
         PORT=suppliedport

      s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      if self.socketOptions is not None:
          s.setsockopt(*self.socketOptions)
      s.setblocking(0)
      assert self.debugger.note("PrimaryListenSocket.makeTCPServerPort", 5, "HOST,PORT",":",HOST,":",PORT,":")
      try:
          s.bind((HOST,PORT))
          s.listen(maxlisten)
      except socket.error:
          return None, None # FIXME: Later versions should potentially consider raising an exception here
                            # FIXME: and failing primarily because this is failing silently - which is
                            # FIXME: probably a BAD thing. cf Zen of Python:
                            # FIXME:          Errors should never pass silently.
                            # FIXME: 
                            # FIXME: We are of course doing this:
                            # FIXME:      Unless explicitly silenced.
                            # FIXME: 
                            # FIXME: But in practice this is probably a bad idea in this case in this way. Really requires
                            # FIXME: a change to ConnectedServer.ServerCore ...
                            # FIXME: That said, "main" below resolves this by passing on the fact that the server socket
                            # FIXME: doesn't exist and shuts down.
      return s,PORT

   def createConnectedSocket(self, sock):
      """\
      Accepts the connection request on the specified socket and returns a
      ConnectedSocketAdapter component for it.
      """
      tries = 0
      maxretries = 10
      gotsock=False
      newsock, addr = sock.accept()  # <===== THIS IS THE PROBLEM
      self.send(newReader(self, ((self, "newconnection"), self.listener)), "_selectorSignal")

      gotsock = True
      newsock.setblocking(0)
###      
      CSA = (self.CSA)(newsock,self.selectorService)
      return newsock, CSA

   def closeSocket(self, shutdownMessage):
      """\
      Respond to a socketShutdown message by closing the socket.

      Sends a removeReader and removeWriter message to the selectorComponent.
      Sends a shutdownCSA(self, theCSA) message to "protocolHandlerSignal" outbox.
      """
      theComponent,(sock,howdied) = shutdownMessage.caller, shutdownMessage.message
      shutdownMessage.caller, shutdownMessage.message = None, None
      shutdownMessage = None
#      print ("SOCKET HANDLERS BEFORE", self.socket_handlers)
#      print ("TCPServer.closeSocket", theComponent,(sock,howdied))
      ### FIXME: Pass on how died as well in TCPServer!
      found = False
      for s in self.socket_handlers:
          if self.socket_handlers[s]==theComponent:
              found = True
              break
      if found:
        sock = s

      if sock is not None:
          theComponent = self.socket_handlers[sock]
          sock.close()

      if theComponent:
          # tell the selector about it shutting down

          self.send(removeReader(theComponent, sock), "_selectorSignal")            
          self.send(removeWriter(theComponent, sock), "_selectorSignal")

          # tell protocol handlers
          self.send(_ki.shutdownCSA(self, theComponent), "protocolHandlerSignal")# "signal")
          # Delete the child component
#          print; print ("DELETING", theComponent)
          self.removeChild(theComponent)
          if sock:
              del self.socket_handlers[sock]
          sock = None

#      print ("***************************************************************************************************************************************")
#      print ("*                                                                                                                                     *")
#      print "*                                                                                                                                     *")
#      print ("SOCKET HANDLERS AFTER", self.socket_handlers)
#      print ("protocolHandlerSignal", self.outboxes["protocolHandlerSignal"])
#      print (type(self.outboxes["protocolHandlerSignal"]))
#      print (type(self.outboxes["protocolHandlerSignal"].storage))
#      print (type(self.outboxes["protocolHandlerSignal"].target))
#      print (type(self.outboxes["protocolHandlerSignal"].target.storage))
#      print ("*                                                                                                                                     *")
#      print ("*                                                                                                                                     *")
#      print ("***************************************************************************************************************************************")
#      print ("CHILDREN", self.children)
#      print ("LINKAGES")
#      import pprint
#      pprint.pprint([str(x) for x in self.postoffice.linkages])

   def anyClosedSockets(self):
      """Check "_feedbackFromCSA" inbox for socketShutdown messages, and close sockets in response."""
      closedSomeSockets=False
      while self.dataReady("_feedbackFromCSA"):
         data = self.recv("_feedbackFromCSA")
#         print ("DATA", data)
         if isinstance( data, _ki.socketShutdown):
            self.closeSocket(data)
         closedSomeSockets=True
         data = None
      return closedSomeSockets

   def handleNewConnection(self):
      """\
      Handle notifications from the selector service of new connection requests.

      Accepts and sets up new connections, wiring them up and passing them on via
      the "protocolHandlerSignal" outbox.
      """
      while self.dataReady("newconnection"):
         data = self.recv("newconnection")
         # If we recieve information on data ready, for a server it means we have a new connection
         # to handle
         try:
            newsock, CSA = self.createConnectedSocket(self.listener)
         except socket.error:
            e = sys.exc_info()[1]
            (errorno,errmsg) = e
            if errorno != errno.EAGAIN:
               if errorno != errno.EWOULDBLOCK:
                  raise e
         else:
             pass

             self.socket_handlers[newsock] = CSA

             self.send(_ki.newCSA(self, CSA, newsock), "protocolHandlerSignal")
             self.send(newReader(CSA, ((CSA, "ReadReady"), newsock)), "_selectorSignal")            
             self.send(newWriter(CSA, ((CSA, "SendReady"), newsock)), "_selectorSignal")            
             self.addChildren(CSA)
             self.link((CSA, "CreatorFeedback"),(self,"_feedbackFromCSA"))
#             return CSA

   def main(self):
       if self.listener is None:
           self.send(shutdownMicroprocess, 'signal') # FIXME: Should probably be producerFinished. 
                                                     # FIXME: (ie advisory that I've finished, rather than
                                                     # FIXME: demand next component to shutdown)
           yield 1
           return  # NOTE: Change from suggested fix. (Simplifies code logic/makes diff smaller)

       selectorService, selectorShutdownService, newSelector = Selector.getSelectorServices(self.tracker)
       if newSelector:
           newSelector.activate()
       self.link((self, "_selectorSignal"),selectorService)
       self.link((self, "_selectorShutdownSignal"),selectorShutdownService)
       self.selectorService = selectorService
       self.selectorShutdownService = selectorShutdownService
       self.send(newReader(self, ((self, "newconnection"), self.listener)), "_selectorSignal")
       yield 1
       while 1:
           if not self.anyReady():
               self.pause()
               yield 1
           if self.anyClosedSockets():
               for i in range(10):
                  yield 1
           self.handleNewConnection() # Data ready means that we have a connection waiting.
           if self.dataReady("control"):
               data = self.recv("control")
               if isinstance(data, serverShutdown):
                   break
           yield 1
       self.send(removeReader(self, self.listener), "_selectorSignal") 
       self.send(shutdown(), "_selectorShutdownSignal")

   def stop(self):
       if self.listener is not None:
           self.send(removeReader(self, self.listener), "_selectorSignal") 
           self.send(shutdown(), "_selectorShutdownSignal")
           self.listener.close() # Ensure we close the server socket. Only really likely to
                                 # be called from the scheduler shutting down due to a stop.
           self.listener = None
       super(TCPServer,self).stop()


__kamaelia_components__  = ( TCPServer, )

if __name__ == '__main__':
   print ("Simple integration test moved out to InternetHandlingTests.py")
