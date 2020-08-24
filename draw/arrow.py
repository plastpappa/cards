import math

from pyglet import shapes as shp

from draw.vector import Vector


class Arrow:
    POINTY_ANGLE = math.pi / 5
    
    def __init__(
        self, posA: Vector, posB: Vector,
        arrow_size: int, offset: int, pad: int,
        colour = (255, 255, 255, 255), stroke_width: int = 2,
        batch = None, group = None
    ):
        self._batch        = batch
        self._group        = group
        self._colour       = colour
        self._stroke_width = stroke_width
        self._posA         = posA
        self._posB         = posB
        self._arrow_size   = arrow_size
        self._offset       = offset
        self._pad          = pad
        
        self.line1  = None
        self.line2  = None
        self.arrow1 = None
        self.arrow2 = None
        self._update()
        
        
    @property
    def posA(self):
        return self._posA
        
    @posA.setter
    def posA(self, posA):
        self._posA = posA
        self._update_line()
        
    @property
    def posB(self):
        return self._posB
        
    @posB.setter
    def posB(self, posB):
        self._posB = posB
        self._update()
    
        
    def _mk_line(self, a: Vector, b: Vector, colour = None):
        line = shp.Line(
            a.x, a.y, b.x, b.y,
            self._stroke_width, self._colour[0:3] if colour is None else colour,
            batch = self._batch, group = self._group
        )
        line.opacity = self._colour[3]
        return line
        
    def _update(self):
        self._update_line()
    
    def _update_line(self):
        self._delete_line()
        
        def div(x, y):
            return math.copysign(1000000000, x) if y == 0 else x / y
            
        d  = self._posB - self._posA
        k  = div(d.y, d.x)
        α  = math.atan2(d.y, d.x)
        q  = Vector(math.cos(α), math.sin(α))
        p  = q * self._pad
        o  = Vector(math.sin(α), -math.cos(α)) * self._offset
        a  = self._posA + p
        b  = self._posB - p
        β  = Arrow.POINTY_ANGLE
        s  = math.sqrt(1 + k**2)
        ka = math.tan(β)
        K1 = div(k + ka, 1 - k * ka)
        K2 = div(k - ka, 1 + k * ka)
        
        def line(O, m, K):
            pos0 = a + O
            x1   = (pos0.y - pos0.x * k - m) / (K - k)
            y1   = K * x1 + m
            return self._mk_line(pos0, Vector(x1, y1))
        
        m1 = b.y - b.x * K1
        m2 = b.y - b.x * K2
        self.line1 = line(o,  m1, K1)
        self.line2 = line(-o, m2, K2)
        
        def arrowline(θ):
            return self._mk_line(b, b - Vector(math.cos(θ), math.sin(θ)) * self._arrow_size)
        
        self.arrow1 = arrowline(α + β)
        self.arrow2 = arrowline(α - β)
    
    
    def delete(self):
        self._delete_line()
        
    def _delete_line(self):
        if self.line1:
            self.line1.delete()
            self.line1 = None
        
        if self.line2:
            self.line2.delete()
            self.line2 = None
            
        if self.arrow1:
            self.arrow1.delete()
            self.arrow1 = None
            
        if self.arrow2:
            self.arrow2.delete()
            self.arrow2 = None
