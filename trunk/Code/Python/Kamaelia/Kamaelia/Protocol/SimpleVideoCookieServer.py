#!/usr/bin/env python2.3
"""
Simple Video based fortune cookie server


To watch the video, on a linux box do this:

netcat <server ip> 1500 | plaympeg -2 -

"""

from Kamaelia.SimpleServerComponent import SimpleServer

from Axon.Component import component, scheduler, linkage, newComponent
from Kamaelia.ReadFileAdaptor import ReadFileAdaptor
import sys

class HelloServer(component):
	Inboxes=["datain","inbox","control"]
	Outboxes=["outbox"]
	maxid = 0
	def __init__(self,filename="Ulysses", debug=0):
		self.filename=filename
		self.debug = debug
		#self.__class__.maxid = self.__class__.maxid + 1
		#id = str(self.__class__) + "_" + str(self.__class__.maxid)
		self.__super.__init__()
#		component.__init__(self, id, inboxes=["datain","inbox"], outboxes=["outbox"])

	def initialiseComponent(self):
		myDataSource = ReadFileAdaptor(filename="/video/buffy-100.mpg",
					readmode="bitrate",
					bitrate=375000, chunkrate=24 )
		linkage(myDataSource,self,"outbox","datain", self.postoffice)
		self.addChildren(myDataSource)

		return newComponent( myDataSource )

	def handleDataIn(self):
		if self.dataReady("datain"):
			data = self.recv("datain")
			if self.debug:
				sys.stdout.write(data)
			self.send(data,"outbox")
		return 1

	def handleInbox(self):
		if self.dataReady("inbox"):
			data = self.recv("inbox")
			self.send(data,"outbox")
		return 1

	def mainBody(self):
		self.handleDataIn()
		self.handleInbox()
		return 1

if __name__ == '__main__':

   SimpleServer(protocol=HelloServer, port=5222).activate()
   # HelloServer(debug = 1).activate()
   scheduler.run.runThreads(slowmo=0)
