#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
====================================================
"Postbox" particle for Axon/Kamaelia visualisation
====================================================

This is an implementation of a rendering particle for "Postbox" particles in
topology visualisation of Axon/Kamaelia systems, representing inboxes/outboxes.



Example Usage
-------------
See Kamaelia.Visualisation.Axon.AxonLaws or
Kamaelia.Visualisation.Axon.AxonVisualiserServer



How does it work?
-----------------
This object subclasses Kamaelia.Physics.Simple.Particle and adds methods to
support rendering. Specifically, rendering to represent an inbox or outbox in 
an Axon/Kamaelia system.

At initialisation, provide a unique ID, a starting (x,y) position tuple, a name
and whether it is an inbox or outbox. The name is abbreviated and displayed as
the particle. 

If the particle becomes selected, then it will render its full name at the top
of the display surface.

At initialisation the label is rendered at several different 45 degree angles.
When rendering, the appropriate one is chosen depending on the directions of
bonds (linkages) this particle is involved in.

It also renders bonds *from* this particle *to* another. Their colour depends
on whether they represent ordinary or passthrough linkages. This is determined
by looking at whether both postbox particles involved are of the same type.

It is assumed that any bonds going *from* this particle *to* another go to
another postbox particle (not a component particle). If this is not the case
then behaviour is undefined.

Rendering is performed by a generator, returned when the render() method is
called. Its behaviour is that needed for the framework for multi-pass rendering
that is used by TopologyViewer.

The generator yields the number of the rendering pass it wishes to be next on
next. Each time it is subsequently called, it performs the rendering required
for that pass. It then yields the number of the next required pass or completes
if there is no more rendering required.

An setOffset() method is also implemented to allow the particles coordinates
to be offset. This therefore makes it possible to scroll the particles around
the display surface.

See TopologyViewer for more details.

"""

from Kamaelia.Visualisation.PhysicsGraph import BaseParticle

import pygame


def abbreviate(string):
    """Abbreviates strings to capitals, word starts and numerics and underscores"""
    out = ""
    prev = ""
    for c in string:
        if c.isupper() or c.isdigit() or c == "_" or c == "." or (c.isalpha() and not prev.isalpha()):
            out += c.upper()
        prev = c
    return string
#    return out

_COMPONENT_RADIUS = 32    


def nearest45DegreeStep( delta ):
    """Returns (in degrees) the nearest 45 degree angle match to the supplied vector.
    
       Returned values are one of 0, 45, 90, 135, 180, 225, 270, 315.       
       If the supplied vector is (0,0), the returned angle is 0.
    """
    dx,dy = delta
    if dx == 0 and dy == 0:
        return 0
    
    # rotate dy and dx by +22.5 degrees,
    # so the boundaries between the 45 degree regions now nicely
    # line up with 0, 45, 90, ... instead of 22.5, 67,5 etc
    
    cos = 0.92387953251128674     # math.cos(math.radians(22.5))
    sin = 0.38268343236508978     # math.sin(math.radians(22.5))
    dx, dy = (dx*cos - dy*sin), (dy*cos + dx*sin)
        
    # lookup angle against properties of dy and dx     
    index = ( dy > 0, dx > 0, abs(dy) > abs(dx) )
    return angleMappings[index]

angleMappings = { (True,  True,  False) : 0,
                  (True,  True,  True ) : 45,
                  (True,  False, True ) : 90,
                  (True,  False, False) : 135,
                  (False, False, False) : 180,
                  (False, False, True ) : 225,
                  (False, True,  True ) : 270,
                  (False, True,  False) : 315 }
            
            
class PPostbox(BaseParticle):
    """\
    PPostbox -> new PPostbox object.
    
    Particle representing an Axon/Kamaelia inbox/outbox for topology
    visualisation.
    
    Keyword arguments:
    
    - position  -- (x,y) tuple of particle coordinates
    - name      -- Name for the inbox/outbox being represented
    - boxtype   -- "inbox" or "outbox"
    """
    
    # mapping of angles to labels
    labelangles =  { 0:2, 45:3, 90:0, 135:1, 180:2, 225:3, 270:0, 315:1 }
    
    # different colours for linkages depending on whether they are passthrough
    # (inbox->inbox, outbox->outbox) or ordinary (inbox<->outbox)
    colours = { ("inbox",  "outbox"):(0,160,0),
                ("outbox", "inbox" ):(0,160,0),
                ("inbox",  "inbox" ):(224,128,0),
                ("outbox", "outbox"):(224,128,0)  }

    def Inbox(ID, position, name):
        """\
        Inbox(ID,position,name) -> new PPostbox object with boxtype "inbox".
        
        Static method.
        """
        return PPostbox(ID=ID, position=position, name=name, boxtype="inbox")
        
    def Outbox(ID, position, name):
        """\
        Outbox(ID,position,name) -> new PPostbox object with boxtype "outbox".
        
        Static method.
        """
        return PPostbox(ID=ID, position=position, name=name, boxtype="outbox")
        
    Inbox  = staticmethod(Inbox)
    Outbox = staticmethod(Outbox)
                
    def __init__(self, ID, position, name, boxtype):
        """x.__init__(...) initializes x; see x.__class__.__doc__ for signature"""
        super(PPostbox,self).__init__(position=position, ID = ID )
        self.name   = name
        self.ptype  = "postbox"
        self.postboxtype = boxtype
        self.left   = 0
        self.top    = 0
        self.radius = 16
        self.buildLabels()
        self.selected = False
        pygame.font.init()        
        
    def buildLabels(self):
        """\
        Pre-renders text labels to surfaces for different 45 degree
        angles.
        
        On exit:
        self.label is a list of surfaces containing rendered labels
        self.slabel is the same but coloured for when the particle is selected
        self.labelxo is a list of x-offsets for each label's centre.
        self.labelyo is a list of y-offsets fo reach label's centre.
        self.desclabel is the description label displayed when selected
        """
        from pygame.transform import rotozoom, rotate
        
        font = pygame.font.Font(None, 14)
        
        label = font.render(" "+abbreviate(self.name)+" ", True, (0,0,0), )
        self.label   = []   # 'selected' labels
        self.labelxo = []
        self.labelyo = []
        self.label.append(rotate(label, 90))
        self.label.append(rotozoom(label, 45, 1.0))
        self.label.append(label)
        self.label.append(rotozoom(label, -45, 1.0))

        slabel = font.render(" "+abbreviate(self.name)+" ", True, (96,96,255), )
        self.slabel  = []
        self.slabel.append(rotate(slabel, 90))
        self.slabel.append(rotozoom(slabel, 45, 1.0))
        self.slabel.append(slabel)
        self.slabel.append(rotozoom(slabel, -45, 1.0))
        
        
        for l in self.label:
            self.labelxo.append( - l.get_width()  / 2 )
            self.labelyo.append( - l.get_height() / 2 )

        font = pygame.font.Font(None, 20)
        self.desclabel = font.render(self.postboxtype.upper()+" : "+self.name, True, (0,0,0), (255,255,255))
                    
            
    def render(self, surface):
        """\
        Multi-pass rendering generator.

        Renders this particle in multiple passes to the specified pygame surface -
        yielding the number of the next pass to be called on between each. Completes
        once it is fully rendered.
        """
   
        direction = (0,0) # default direction for the text label
        
        yield 1
        x = int(self.pos[0] - self.left)
        y = int(self.pos[1] - self.top )
        for p in self.bondedTo:
            endx = int(p.pos[0] - self.left)
            endy = int(p.pos[1] - self.top)
            
            colour = PPostbox.colours[ (self.postboxtype, p.postboxtype) ]
            
            pygame.draw.line(surface, colour, (x,y),  (endx,endy) )
            
            # draw a pwetty arrow on the line, showing the direction
            mid = ( (x+endx*3)/4, (y+endy*3)/4 )
            
            direction = ( (endx-x), (endy-y) )
            length    = ( direction[0]**2 + direction[1]**2 )**0.5
            direction = [ 6*n / length for n in direction ]
            
            norm      = ( -direction[1], direction[0] )
            
            leftarrow  = ( mid[0] - direction[0] - norm[0], mid[1] - direction[1] - norm[1] )
            rightarrow = ( mid[0] - direction[0] + norm[0], mid[1] - direction[1] + norm[1] )
            
            pygame.draw.line(surface, colour, mid, leftarrow  )
            pygame.draw.line(surface, colour, mid, rightarrow )
        
        yield 3
        # if we've not got a 'direction' yet for the text label (from bonds 'from' this node )
        # then look at bonds 'to' this node from other nodes of the same type
        if direction==(0,0):
            for p in self.bondedFrom:
                if p.ptype == self.ptype:
                    endx = int(p.pos[0] - self.left)
                    endy = int(p.pos[1] - self.top)
                    direction = ( (endx-x), (endy-y) )
        
        # render name label, tilted along the 'direction'
        i = PPostbox.labelangles[ nearest45DegreeStep(direction) ]
        if self.selected:
            l = self.slabel[i]
        else:
            l = self.label[i]
        surface.blit(l, ( x + self.labelxo[i], y + self.labelyo[i] ) )

        if self.selected:
            yield 10
            surface.blit(self.desclabel, (72,16) )

                                 
    def setOffset( self, offset ):
        """\
        Set the offset of the top left corner of the rendering area.

        If this particle is at (px,py) it will be rendered at (px-x,py-y).
        """
        x,y = offset
        self.left = x
        self.top  = y
                     
    def select( self ):
        """Tell this particle it is selected."""
        self.selected = True

    def deselect( self ):
        """Tell this particle it is deselected."""
        self.selected = False
