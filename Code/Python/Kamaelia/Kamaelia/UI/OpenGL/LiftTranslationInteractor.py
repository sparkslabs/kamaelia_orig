#!/usr/bin/env python
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
===========================
Lift Translation Interactor
===========================

An interactor for moving OpenGLComponents corresponding to mouse
movement along the X,Y plane. When "grabbing" an object it is lifted by
a specified amount.

LiftTranslationInteractor is a subclass of Interactor.

Example Usage
-------------
The following example shows four SimpleCubes which can be moved by
dragging your mouse::

    o1 = SimpleCube(position=(6, 0,-30), size=(1,1,1), name="center").activate()
    i1 = LiftTranslationInteractor(target=o1).activate()

    o2 = SimpleCube(position=(0, 0,-30), size=(1,1,1), name="center").activate()
    i2 = LiftTranslationInteractor(target=o2).activate()

    o3 = SimpleCube(position=(-3, 0,-30), size=(1,1,1), name="center").activate()
    i3 = LiftTranslationInteractor(target=o3).activate()

    o4 = SimpleCube(position=(15, 0,-30), size=(1,1,1), name="center").activate()
    i4 = LiftTranslationInteractor(target=o4).activate()

    Axon.Scheduler.scheduler.run.runThreads()  

How does it work?
-----------------
LiftTranslationInteractor is a subclass of Interactor. It overrides
the __ini__(), setup(), handleEvents() and frame() methods.

The matched movement works by using the position of the controlled
object and determine its X,Y-aligned plane. The amount of mouse movement
is then calculated as if it was on this plane. This is done by
intersecting the direction vector which is included in the mouse event
with the plane to get the point of intersection. Then the distance
between the newly generated point and the last point is calculated. The
result is the actual amount of movement along the X and the Y axis.

The interactor makes all the linkages it needs during initialisation.
Because the interactor needs the actual position of the controlled
component to be accurate all the time, it uses the components "position"
outbox by default. If you don't want the interactor to make the
linkages, you can set nolink=True as constructor argument. The following
linkages are needed for the interactor to work (from the interactors
point of view)::

    self.link( (self, "outbox"), (self.target, "rel_position") )
    self.link( (self.target, "position"), (self, "inbox") )

"""


import pygame

import Axon
from .Intersect import Intersect
from .Interactor import Interactor

class LiftTranslationInteractor(Interactor):
    """\
    LiftTranslationInteractor(...) -> A new LiftTranslationInteractor component.
    
    An interactor for moving OpenGLComponents corresponding to mouse
    movement along the X,Y plane. When "grabbing" an object it is lifted by
    a specified amount.
    
    Keyword arguments:
    
    - liftheight    -- height by which the controlled object is lifted (default=2)
    """
    
    def __init__(self, **argd):
        """x.__init__(...) initializes x; see x.__class__.__doc__ for signature"""
        super(LiftTranslationInteractor, self).__init__(**argd)

        self.liftheight = argd.get("liftheight", 2)
                                         
        self.grabbed = False
        self.position = None
        self.oldpoint = None

        if self.nolink == False:
            self.link( (self, "outbox"), (self.target, "rel_position") )
            self.link( (self.target, "position"), (self, "inbox") )


    def setup(self):
        self.addListenEvents( [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP ])


    def handleEvents(self):
        while self.dataReady("events"):
            event = self.recv("events")
            
            if self.position is not None:
                if event.type == pygame.MOUSEBUTTONDOWN or pygame.MOUSEMOTION and self.grabbed:
                    p1 = self.position.copy()
                    p1.x += 10
                    p2 = self.position.copy()
                    p2.y += 10
                    z = Intersect.ray_Plane(event.viewerposition, event.direction, [self.position, p1, p2])
                    newpoint = event.direction * z
                    
                if event.type == pygame.MOUSEBUTTONDOWN and self.identifier in event.hitobjects:
                    if event.button == 1:
                        self.grabbed = True
                        self.send((0,0,self.liftheight), "outbox")
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.grabbed:
                        self.grabbed = False
                        self.send((0,0,-self.liftheight), "outbox")
                if event.type == pygame.MOUSEMOTION:
                    if self.grabbed == True:
                        if self.oldpoint is not None:
                            diff = newpoint-self.oldpoint
                            diff.z = 0
                            self.send(diff.toTuple(), "outbox")

                try:
                    self.oldpoint = newpoint
                except NameError: pass            


    def frame(self):
        while self.dataReady("inbox"):
            self.position = Vector(*self.recv("inbox"))


__kamaelia_components__ = ( LiftTranslationInteractor, )

if __name__=='__main__':
    from SimpleCube import SimpleCube

    o1 = SimpleCube(position=(6, 0,-30), size=(1,1,1), name="center").activate()
    i1 = LiftTranslationInteractor(target=o1).activate()

    o2 = SimpleCube(position=(0, 0,-30), size=(1,1,1), name="center").activate()
    i2 = LiftTranslationInteractor(target=o2).activate()

    o3 = SimpleCube(position=(-3, 0,-30), size=(1,1,1), name="center").activate()
    i3 = LiftTranslationInteractor(target=o3).activate()

    o4 = SimpleCube(position=(15, 0,-30), size=(1,1,1), name="center").activate()
    i4 = LiftTranslationInteractor(target=o4).activate()
    
    Axon.Scheduler.scheduler.run.runThreads()  
# Licensed to the BBC under a Contributor Agreement: THF
