#!/usr/bin/env python

import Axon
from Axon.Component import component
from Axon.Ipc import producerFinished, shutdownMicroprocess

class ReadFileAdapter(component):
   """Provides read access to a file.
      You request numbers of bytes/lines of data.
      Data is returned in response.
      
      Bytes returned as a single string
      Line(s) returned as a **list** of strings
      
      Shuts down in response to a shutdownMicroprocess message
   """
   Inboxes = { "inbox" : "requests to 'n' read bytes/lines",
               "control" : ""
             }
   Outboxes = { "outbox" : "data output"
                "signal" : "outputs 'producerFinished' after all data has been read"
              }

   def __init__(self, filename, readmode="bytes"):
       """Initialisation
       
          filename = name of file to read data from
          readmode = "bytes" to read in 'n' byte chunks
                   = "lines" to read 'n' line chunks
                      ('n' sent to inbox to request the data)
       """
       super(ReadFileAdapter, self).__init__()
       
       if readmode == "bytes":
          self.read = readNBytes
       elif:
          self.read = readNLines
       else:
           raise ValueError("readmode must be 'bytes' or 'lines'")
       
       self.file = open(filename, "rb",0)
       
       
   def readNBytes(n):
       data = self.file.read(n)
       if not data:
           raise "EOF"
       return data
   
   
   def readNLines(n)
       data = self.file.readlines(n)
       if not data:
           raise "EOF"
       return data
   
          
   def main(self):
       done = False
       while not done:
           yield 1
           
           if self.dataReady("inbox"):
               n = int(self.recv("inbox"))
               try:
                   data = self.read(n)
                   self.send(data,"outbox")
               except:
                   self.send(producerFinished(self), "signal")
           
           if self.shutdown():
               done = True
           else:
               self.pause()

               
   def shutdown(self)
      if self.dataReady("control"):
          msg = self.recv("control")
          if isinstance(msg, shutdownMicroprocess):
              self.send(msg, "signal")
              return True
      return False
      
               
   def closeDownComponent(self):
      self.file.close()

      
      
if __name__ == "__main__":
    pass