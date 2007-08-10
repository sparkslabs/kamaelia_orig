#!/usr/bin/python

import pygame
import Axon
from Kamaelia.UI.GraphicDisplay import PygameDisplay
from Axon.Ipc import WaitComplete
import time

class PygameComponent(Axon.Component.component):
   Inboxes = { "inbox"        : "Specify (new) filename",
               "control"      : "Shutdown messages & feedback from Pygame Display service",
               "alphacontrol" : "Transparency of the ticker (0=fully transparent, 255=fully opaque)",
               "pausebox"     : "Any message pauses the ticker",
               "unpausebox"   : "Any message unpauses the ticker",
             }
   Outboxes = { "outbox" : "NOT USED",
                "signal" : "Shutdown signalling & sending requests to Pygame Display service",
              }
   def waitBox(self,boxname):
      """Generator. yields 1 until data ready on the named inbox."""
      while True:
         if self.dataReady(boxname): return
         else: yield 1

   def flip(self):
       self.send({"REDRAW":True, "surface":self.display}, "signal")

   def requestDisplay(self, **argd):
      """\
      Generator. Gets a display surface from the Pygame Display service.

      Makes the request, then yields 1 until a display surface is returned.
      """
      displayservice = PygameDisplay.getDisplayService()
      self.link((self,"signal"), displayservice)
      self.send(argd, "signal")
      for _ in self.waitBox("control"): yield 1
      display = self.recv("control")
      self.display = display

   def handleAlpha(self):
       if self.dataReady("alphacontrol"):
            alpha = self.recv("alphacontrol")
            self.display.set_alpha(alpha)

   def doRequestDisplay(self,size):
        return WaitComplete(
                 self.requestDisplay(DISPLAYREQUEST=True,
                                     callback = (self,"control"),
                                     size = size,
                                     position = (0,0)
                 )
               )
   def clearDisplay(self):
       """Clears the ticker of any existing text."""
       self.display.fill(0xffffff)


class MyFoo(PygameComponent):
    def makeLabel(self, text):
        font = pygame.font.Font(None, 14)
        textimage = font.render(text,True, (0,0,0),)
        (w,h) = textimage.get_size()
        return textimage, w,h

    def drawBox(self, box):
        print "Drawing box", box
        pygame.draw.rect(self.display, 0xaaaaaa, (self.boxes[box],self.boxsize), 0)
        cx = self.boxes[box][0]+self.boxsize[0]/2
        cy = self.boxes[box][1]+self.boxsize[1]/2
        image, w,h = self.makeLabel(self.nodes[box])
        self.display.blit( image, (cx-w/2,cy-h/2) )
        if box in self.topology:
           self.drawTree(box)
   
    def drawLine(self, line):
        print line[0],line[1]
        pygame.draw.line(self.display, 0,line[0],line[1],2)

    def drawTree(self, tree):
#        paths = self.trees[tree]
        box = tree
        w = self.boxsize[0]
        h = self.boxsize[1]
        x,y = self.boxes[box]
        paths = []
        for subbox in self.topology[box]:
            ax,ay = self.boxes[subbox]
            paths.append(
                    [
                        (((x+w/2), y+h) , ((x+w/2), y+h+((ay-(y+h))/2) )),
                        (((x+w/2), y+h+((ay-(y+h))/2) ), ((ax+w/2), ay-(ay-(y+h))/2 )),
                        (((ax+w/2), ay) , ((ax+w/2), ay-(ay-(y+h))/2 )),
                    ],
            )
        
        for path in paths:
            self.drawPath(path)

    def drawPath(self, path):
        for line in path:
            print line
            self.drawLine(line)
    
    def main(self):
        """Main loop."""
        yield self.doRequestDisplay((1024, 768))
        self.clearDisplay()
        self.flip()
        for box in self.boxes:
            self.drawBox(box)
        self.flip()
        while 1:
            yield 1

class MyBoxes(MyFoo):
    boxsize = (100,50)
    nodes = {
       1: "MagnaDoodle",
       2: "init",
       3: "setupdisplay",
       4: "mainloop",
       5: "exit",
       6: "Get Display Surface",
       7: "Set Event Options",
       8: "Handle Shutdown",
       9: "Loop pygame events",
      10: "handle event",
      11: "mouse dn 1",
      12: "mouse dn 2",
      13: "mouse dn 3",
    }
    topology = {
        1: [ 2, 3, 4, 5],
        3: [ 6, 7],
        4: [ 8, 9],
        9: [ 10],
        10: [ 11, 12, 13],
    }
    boxes = {
        1: (400, 100),
        2: (75, 200),
        3: (225, 200),
        4: (525, 200),
        5: (675, 200),
        6: (150, 300),
        7: (300, 300),
        8: (450, 300),
        9: (600, 300),
       10: (600, 400),
       11: (450, 500),
       12: (600, 500),
       13: (750, 500),
    }

MyBoxes().run()



