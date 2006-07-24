#!/usr/bin/env python
#
# (C) 2005 British Broadcasting Corporation and Kamaelia Contributors(1)
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
"""\
=====================
General 3D Object
=====================
Methods to be overridden:
    init()
    draw()
    handleEvents()
"""


import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import Axon
from Util3D import *
from Display3D import Display3D

class Object3D(Axon.Component.component):
    Inboxes = {
       "inbox": "not used",
       "control": "ignored",
       "callback": "for the response after a displayrequest",
        "position" : "receive position triple (x,y,z)",
        "rotation": "receive rotation triple (x,y,z)",
        "scaling": "receive scaling triple (x,y,z)",
        "rel_position" : "receive position triple (x,y,z)",
        "rel_rotation": "receive rotation triple (x,y,z)",
        "rel_scaling": "receive scaling triple (x,y,z)",
    }
    
    Outboxes = {
        "outbox": "used for sending position information",
        "display_signal" : "Outbox used for communicating to the display surface",
        "position" : "send position status when updated",
        "rotation": "send rotation status when updated",
        "scaling": "send scaling status when updated"
    }
    
    def __init__(self, **argd):
        super(Object3D, self).__init__()

        # transformation data
        self.size = argd.get("size", Vector(2,2,2))
        self.pos = argd.get("pos",Vector(0,0,-15))
        self.rot = Vector(0.0,0.0,0.0)
        self.scaling = argd.get("scaling",Vector(1,1,1))
        self.transform = Transform()
        
        # for detection of changes
        self.oldrot = Vector()
        self.oldpos = Vector()
        self.oldscaling = Vector()

        # name        
        self.name = argd.get("name", "nameless")

                                          
    def applyTransforms(self):
        # generate new transformation matrix if needed
        if self.oldscaling != self.scaling or self.oldrot != self.rot or self.oldpos != self.pos:
            self.transform.reset()
            self.transform.applyScaling(self.scaling)
            self.transform.applyRotation(self.rot)
            self.transform.applyTranslation(self.pos)

            if self.oldscaling != self.scaling:
                self.send(self.scaling, "scaling")
                self.oldscaling = self.scaling.copy()

            if self.oldrot != self.rot:
                self.send(self.rot, "rotation")
                self.oldrot = self.rot.copy()

            if self.oldpos != self.pos:
                self.send(self.pos, "position")
                self.oldpos = self.pos.copy()


    def handleMovement(self):
        while self.dataReady("position"):
            pos = self.recv("position")
            self.pos = Vector(*pos)
        
        while self.dataReady("rotation"):
            rot = self.recv("rotation")
            self.rot = Vector(*rot)
            
        while self.dataReady("scaling"):
            scaling = self.recv("scaling")
            self.scaling = Vector(*scaling)
            
        while self.dataReady("rel_position"):
            self.pos += Vector(*self.recv("rel_position"))
            
        while self.dataReady("rel_rotation"):
            self.rot += Vector(*self.recv("rel_rotation"))
            
        while self.dataReady("rel_scaling"):
            self.scaling = Vector(*self.recv("rel_scaling"))
            
            
    def handleEvents(self):
        pass        


    def draw(self):
        print "HALLO"
        pass


    def main(self):
        # get display service
        displayservice = Display3D.getDisplayService()
        
        # display list id
        self.displaylist = glGenLists(1);

        # draw object to its displaylist
        print "list", self.displaylist
        glNewList(self.displaylist, GL_COMPILE)
        self.draw()
        glEndList()
        
        # create display request
        self.disprequest = { "3DDISPLAYREQUEST" : True,
                                          "callback" : (self,"callback"),
                                          "events" : (self, "inbox"),
                                          "size": self.size,
                                          "displaylist": self.displaylist,
                                          "transform": self.transform}
    
        # send display request
        self.link((self,"display_signal"), displayservice)
        self.send(self.disprequest, "display_signal");

#        for _ in self.waitBox("callback"): yield 1
#        response = self.recv("callback")
#        self.ident = response.ident

        while 1:
            yield 1
            self.applyTransforms()
            self.handleMovement()
            self.handleEvents()


if __name__=='__main__':
    o1 = Object3D(pos=Vector(2, 0,-12), name="center").activate()
    o2 = Object3D(pos=Vector(3, 1,-12), name="right").activate()
    o3 = Object3D(pos=Vector(-4, 0,-12), name="left").activate()
    Axon.Scheduler.scheduler.run.runThreads()  
