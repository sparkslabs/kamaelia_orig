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
            
            
class PRelation(BaseParticle):

    # mapping of angles to labels
    labelangles =  { 0:2, 45:3, 90:0, 135:1, 180:2, 225:3, 270:0, 315:1 }

    # different colours for linkages depending on whether they are passthrough
    # (relation->relation, outbox->outbox) or ordinary (relation<->outbox)
    colours = {# ("relation",  "outbox"):(0,160,0),
               # ("outbox", "relation" ):(0,160,0),
                ("relation",  "relation" ):(224,128,0),
               # ("outbox", "outbox"):(224,128,0)
              }

    def Relation(ID, position, name):
        """\
        Relation(ID,position,name) -> new PRelation object with boxtype "relation".

        Static method.
        """
        return PRelation(ID=ID, position=position, name=name, boxtype="relation")

#    def Outbox(ID, position, name):
#        """\
#        Outbox(ID,position,name) -> new PRelation object with boxtype "outbox".
#
#        Static method.
#        """
#        return PRelation(ID=ID, position=position, name=name, boxtype="outbox")

    Relation  = staticmethod(Relation)
#    Outbox = staticmethod(Outbox)

    def __init__(self, ID, position, name, boxtype):
        """x.__init__(...) initializes x; see x.__class__.__doc__ for signature"""
        super(PRelation,self).__init__(position=position, ID = ID )
        self.name   = name
        self.ptype  = "relation"
        self.relationtype = boxtype
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

#        print self.slabel[0].get_width(),self.slabel[0].get_height()

        self.radius = max(self.slabel[0].get_width(),self.slabel[0].get_height())/2
#        self.radius = max(self.slabel[0].get_width(),self.slabel[0].get_height())

        for l in self.label:
            self.labelxo.append( - l.get_width()  / 2 )
            self.labelyo.append( - l.get_height() / 2 )

        font = pygame.font.Font(None, 20)
        self.desclabel = font.render(self.relationtype.upper()+" : "+self.name, True, (0,0,0), (255,255,255))


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

            colour = PRelation.colours[ (self.relationtype, p.relationtype) ]

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
        i = PRelation.labelangles[ nearest45DegreeStep(direction) ]

        colour = (255,255,255)
        bordercolour = (192,192,192)
        if self.selected:
            colour = (160,160,255)
            bordercolour = (224,0,0)

        R = int(self.radius*1.3 - self.radius)
        if R < 5:
            R = 5
        x_radius = self.radius+R
        y_radius = x_radius/2
        if y_radius > 20:
            y_radius = 20
        points = [
                (x-x_radius,y),
                (x,y+y_radius),
                (x+x_radius,y),
                (x,y-y_radius),
        ]
        points = [
                (x-24,y),
                (x,y+16),
                (x+24,y),
                (x,y-16),
        ]
#        pygame.draw.polygon(surface, colour, points)
        pygame.draw.polygon(surface, (255,255,255), points)
        pygame.draw.polygon(surface, bordercolour, points,1)

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
