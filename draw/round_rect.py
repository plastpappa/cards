import math

from pyglet import shapes as shp
from pyglet.gl import GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from pyglet.gl import GL_TRIANGLES, GL_LINES, GL_BLEND
from pyglet.graphics import Batch

from draw.vector import Vector


class BetterArc(shp.Arc):
    def __init__(
        self, pos: Vector, radius: int,
        segments = 25, angle = math.pi * 2, colour = (255, 255, 255, 255),
        batch = None, group = None
    ):
        self._pos = pos
        self._radius = radius
        self._segments = segments
        self._colour = colour
        self._angle = angle
        self._anchor = Vector(0, 0)

        self._batch = batch or Batch()
        self._group = shp._ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, group)
        
        self._vertex_list = self._batch.add(
            (self._segments - 1) * 2,
            GL_LINES, self._group, 'v2f', 'c4B'
        )
        self._update_position()
        self._update_color()
    
    def _update_position(self):
        x = self._pos.x + self._anchor.x
        y = self._pos.y + self._anchor.y
        r = self._radius
        tau_segs = self._angle / (self._segments - 1)

        # Calcuate the outer points of the arc:
        points = [ (x + (r * math.cos(i * tau_segs)),
                    y + (r * math.sin(i * tau_segs)))
                   for i in range(self._segments) ]

        # Create a list of doubled-up points from the points:
        vertices = []
        for i, point in enumerate(points[1:]):
            line_points = *points[i], *point
            vertices.extend(line_points)
                
        self._vertex_list.vertices[:] = vertices
    
    def _update_color(self):
        self._vertex_list.colors[:] = self._colour * (self._segments - 1) * 2
