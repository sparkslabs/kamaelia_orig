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
============
Progress Bar
============

A progress bar widget for the OpenGL display service.

This component is a subclass of OpenGLComponent and therefore uses the
OpenGL display service.

Example Usage
-------------
A progress bar with changing value::

    Graphline(
        BOUNCE = bouncingFloat(0.5),
        PROGRESS = ProgressBar(size = (3, 0.5, 0.2), position=(0,0,-10), progress=0.5),
        linkages = {
            ("BOUNCE", "outbox"):("PROGRESS", "progress"),
        }
    ).run()

How does it work?
-----------------
ProgressBar is a subclass of OpenGLComponent (for OpenGLComponent
functionality see its documentation). It overrides __init__(), draw(),
handleEvents() and frame().

This component basically draws a cuboid shaped cage and inside of it a
transparent bar indicating a percentage.

The percentage values are received at the "progress" inbox. The values
must be in the range [0,1]. If the value is 0.0, the bar is not drawn at
all, if 1.0 the bar has its maximum length. Received values which lie
outside of this range are clamped to it.

Because the progress bar is transparent, the widget has to be drawn in a
special order. First, the cage is drawn normally. Then the depth buffer
is made read only and the transparent bar is drawn.
"""


import Axon
import pygame

from OpenGL.GL import glBegin, glPolygonMode, glEnable, glDepthMask, glBlendFunc, glColor4f, glVertex3f, glEnd, glDepthMask, glDisable
from OpenGL.GL import GL_BLEND, GL_QUADS, GL_FRONT_AND_BACK, GL_FILL, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_FALSE, GL_TRUE

from .Vector import Vector
from .OpenGLComponent import OpenGLComponent


class ProgressBar(OpenGLComponent):
    """\
    ProgressBar(...) -> new ProgressBar component.

    Create a progress bar widget using the OpenGLDisplay service. Shows
    a tranparent bar indicating a percentage.
    
    Keyword arguments:
    
    - cagecolour  -- Cage colour (default=(0,0,0))
    - barcolour   -- Bar colour (default=(200,200,244))
    - progress    -- Initial progress value (default=0.0)
    """
    def __init__(self, **argd):
        """x.__init__(...) initializes x; see x.__class__.__doc__ for signature"""
        super(ProgressBar, self).__init__(**argd)
        
        # add progress Inbox, used for reception of progress values in the range (0,1)
        self.addInbox("progress")

        # appearance        
        self.edgecolour = argd.get("edgecolour", (0,0,0))
        self.barcolour = argd.get("barcolour", (200,200,244))

        #progress (1.0 is full)
        self.progress = argd.get("progress", 0.0)
                

    def draw(self):
        hs = self.size/2.0

        progw = self.size.x * self.progress
        
        # draw envelope
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBegin(GL_QUADS)
        glColor4f(self.edgecolour[0]/256.0, self.edgecolour[1]/256.0, self.edgecolour[2]/256.0, 0.8)
        # right
        glVertex3f(hs.x,hs.y,hs.z)
        glVertex3f(hs.x,-hs.y,hs.z)
        glVertex3f(hs.x,-hs.y,-hs.z)
        glVertex3f(hs.x,hs.y,-hs.z)
        # left
        glVertex3f(-hs.x,hs.y,hs.z)
        glVertex3f(-hs.x,-hs.y,hs.z)
        glVertex3f(-hs.x,-hs.y,-hs.z)
        glVertex3f(-hs.x,hs.y,-hs.z)
        # top
        glVertex3f(hs.x,hs.y,hs.z)
        glVertex3f(-hs.x,hs.y,hs.z)
        glVertex3f(-hs.x,hs.y,-hs.z)
        glVertex3f(hs.x,hs.y,-hs.z)
        # bottom
        glVertex3f(hs.x,-hs.y,hs.z)
        glVertex3f(-hs.x,-hs.y,hs.z)
        glVertex3f(-hs.x,-hs.y,-hs.z)
        glVertex3f(hs.x,-hs.y,-hs.z)
        glEnd()
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        if self.progress > 0.0:
            # draw progress
            glEnable(GL_BLEND)
            # make depth buffer read only
            glDepthMask(GL_FALSE)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBegin(GL_QUADS)
            glColor4f(self.barcolour[0]/256.0, self.barcolour[1]/256.0, self.barcolour[2]/256.0, 0.5)
            
            # front
            glVertex3f(-hs.x+progw,hs.y,hs.z)
            glVertex3f(-hs.x+progw,-hs.y,hs.z)
            glVertex3f(-hs.x,-hs.y,hs.z)
            glVertex3f(-hs.x,hs.y,hs.z)
            # back
            glVertex3f(-hs.x+progw,hs.y,-hs.z)
            glVertex3f(-hs.x+progw,-hs.y,-hs.z)
            glVertex3f(-hs.x,-hs.y,-hs.z)
            glVertex3f(-hs.x,hs.y,-hs.z)
            # right
            glVertex3f(-hs.x+progw,hs.y,hs.z)
            glVertex3f(-hs.x+progw,-hs.y,hs.z)
            glVertex3f(-hs.x+progw,-hs.y,-hs.z)
            glVertex3f(-hs.x+progw,hs.y,-hs.z)
            # left
            glVertex3f(-hs.x,hs.y,hs.z)
            glVertex3f(-hs.x,-hs.y,hs.z)
            glVertex3f(-hs.x,-hs.y,-hs.z)
            glVertex3f(-hs.x,hs.y,-hs.z)
            # top
            glVertex3f(-hs.x+progw,hs.y,hs.z)
            glVertex3f(-hs.x,hs.y,hs.z)
            glVertex3f(-hs.x,hs.y,-hs.z)
            glVertex3f(-hs.x+progw,hs.y,-hs.z)
            # bottom
            glVertex3f(-hs.x+progw,-hs.y,hs.z)
            glVertex3f(-hs.x,-hs.y,hs.z)
            glVertex3f(-hs.x,-hs.y,-hs.z)
            glVertex3f(-hs.x+progw,-hs.y,-hs.z)
            glEnd()
            glDepthMask(GL_TRUE)
            glDisable(GL_BLEND)

        
    def frame(self):
        self.handleProgress()


    def handleProgress(self):
         while self.dataReady("progress"):
            self.progress = self.recv("progress")
            if self.progress < 0.0: self.progress = 0.0
            if self.progress > 1.0: self.progress = 1.0
            self.redraw()
            

__kamaelia_components__ = (ProgressBar,)

if __name__=='__main__':
    from Kamaelia.Automata.Behaviours import bouncingFloat
    from Kamaelia.Chassis.Graphline import Graphline

    Graphline(
        BOUNCE = bouncingFloat(0.5),
        PROGRESS = ProgressBar(size = (3, 0.5, 0.2), position=(0,0,-10), progress=0.5),
        linkages = {
            ("BOUNCE", "outbox"):("PROGRESS", "progress"),
        }
    ).run()
# Licensed to the BBC under a Contributor Agreement: THF
