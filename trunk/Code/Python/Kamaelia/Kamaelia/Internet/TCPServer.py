#!/usr/bin/env python2.3
#
# TCP Server Socket class
#
# The TCP Server component provides a component for building a TCP based
# network server. You specify a single port number, the system then hunts
# for a selector process, and waits for new connection messages from the
# selector.
#
# When the Server recieves a new connection it performs an accept, and creates
# a connected socket adaptor (CSA) to handle the activity on that connection. This
# CSA is then passed to the TCP Server's protocolHandlerSignal outbox.
# (Internally the CSA is also currently handed over to a selector service to perform
# activity checking)
#
# Inboxes:
#    * DataReady - Data ready on a server socket means the TCP server should
#                    accept a new connection.
#    * _csa_feedback - We recieve feedback from Connected Socket adaptors
#                    on this inbox. Currently this feedback is limited to connection
#                    shutdown messages.
#
# Outboxes:
#    * protocolHandlerSignal - This is used to send a connected socket adaptor
#                    component back to the protocol handler level.
#    * signal - Used to communiate with the selector sending either NewCSA
#                    messages
#
# The client using the TCPServer is then expected to deal with the input/output
# required directly with the CSA. (See SimpleServer component example)
#
# Essentially the steps are:
#    * Create a TCP Server
#    * Wait for CSA messages from the TCP Server
#    * Send what you like to CSA's, ensure you recieve data from the CSAs
#    * Send shutdown messages when done.

import socket, random, Axon, socketConstants, Selector
import Kamaelia.KamaeliaIPC as _ki
from Kamaelia.Internet.ConnectedSocketAdapter import ConnectedSocketAdapter

_component = Axon.Component.component
status = Axon.Ipc.status
wouldblock = Axon.Ipc.wouldblock

class TCPServer(_component):
   Inboxes=["DataReady", "_csa_feedback"]
   Outboxes=["protocolHandlerSignal", "signal"]

   def __init__(self,listenport):
      self.__super.__init__()
      self.listenport = listenport
      self.listener,junk = self.makeTCPServerPort(listenport, maxlisten=5)
      print "TCPS: SERVER INITIALISED"
      import os
      os.system("netstat -natp")
      print "TCPS: PORT", listenport

   def makeTCPServerPort(self, suppliedport=None, HOST=None, minrange=2000,maxrange=50000, maxlisten=5):
      if HOST is None: HOST=''
      if suppliedport is None:
         PORT=random.randint(minrange,maxrange) # Built in support for testing
      else:
         PORT=suppliedport

      s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.setblocking(0)
      assert self.debugger.note("PrimaryListenSocket.makeTCPServerPort", 5, "HOST,PORT",":",HOST,":",PORT,":")
      s.bind((HOST,PORT))
      s.listen(maxlisten)
      return s,PORT

   def createConnectedSocket(self, sock):
      newsock, addr = sock.accept()
      newsock.setblocking(0)
      CSA = ConnectedSocketAdapter(newsock)
      return CSA

   def closeSocket(self, shutdownMessage):
      theComponent,sock = shutdownMessage.caller, shutdownMessage.message
      sock.close()
      # Tell the selector that the socket is no longer valid
      self.send(_ki.shutdownCSA(self, (theComponent,sock)), "signal")
      # Delete the child component
      self.removeChild(theComponent)
      print "TCPS: SHUTTING DOWN SERVER SOCKET"

   def checkForClosedSockets(self):
      if self.dataReady("_csa_feedback"):
         data = self.recv("_csa_feedback")
         if isinstance( data, _ki.socketShutdown):
            self.closeSocket(data)

   def initialiseComponent(self):
      """ What else do we do with a selector?
        * We want it to send us messages when our listen socket is ready.
        * These messages tell us that a new connection is ready, and we should do
          something with it. Anything else? Not yet.
        * Client creates a link from it's own internal linkages to the selector service.
        * Then sends the selector service a message.
        * Basically the same idiom needed here.
      """
      selectorService, newSelector = Selector.selectorComponent.getSelectorService(self.tracker)
      if newSelector:
         self.addChildren(newSelector)
      self.link((self, "signal"),selectorService)
      self.send(_ki.newServer(self, (self,self.listener)), "signal")
      print self.outboxes["signal"]
      return Axon.Ipc.newComponent(*(self.children))

   def handleNewConnection(self):
      if self.dataReady("DataReady"):
         data = self.recv("DataReady")
         # If we recieve information on data ready, for a server it means we have a new connection
         # to handle
         try:
            CSA = self.createConnectedSocket(self.listener)
            self.send(_ki.newCSA(self, CSA), "protocolHandlerSignal")
            self.addChildren(CSA)
            self.link((CSA, "FactoryFeedback"),(self,"_csa_feedback"))
            self.send(_ki.newCSA(CSA, (CSA,CSA.socket)), "signal")
            return CSA
         except socket.error, e:
            (errno,errmsg) = e
            if errno != socketConstants.EAGAIN:
               raise e

   def mainBody(self):
      self.pause()
      self.checkForClosedSockets()
      self.handleNewConnection() # Data ready means that we have a connection waiting.
      return status("ready")

if __name__ == '__main__':
   print "Simple integration test moved out to InternetHandlingTests.py"
