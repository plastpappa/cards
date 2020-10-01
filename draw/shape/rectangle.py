from draw.vector import Vector
from .shape import Shape


class RectangleShape(Shape):
    def __init__(
        self, size: Vector,
        bottom_left: Vector = None, centre: Vector = None
    ):
        self.size = size
        
        if bottom_left is not None:
            self.bottom_left = bottom_left
            self.centre      = bottom_left + size // 2
        elif centre is not None:
            self.centre      = centre
            self.bottom_left = centre - size // 2
        else:
            raise ValueError("Must provide either centre or bottom_left")
        
        self.top_right                 = self.bottom_left + self.size
        self._low_x,    self._low_y    = self.bottom_left
        self._centre_x, self._centre_y = self.centre
        self._high_x,   self._high_y   = self.top_right
        
        self.centre_left   = Vector(self.low_x,    self.centre_y)
        self.top_left      = Vector(self.low_x,    self.high_y)
        self.bottom_right  = Vector(self.high_x,   self.low_y)
        self.centre_right  = Vector(self.high_x,   self.centre_y)
        self.top_centre    = Vector(self.centre_x, self.high_y)
        self.bottom_centre = Vector(self.centre_x, self.low_y)


    @property
    def low_x(self):
        return self._low_x
        
    @low_x.setter
    def low_x(self, low_x):
        self._low_x = low_x
        self.bottom_left.x = low_x
        self.centre_left.x = low_x
        self.top_left.x    = low_x
        
        self.size.x = self._high_x - low_x
        self._set_centre_x(low_x + self.size.x // 2)

    @property
    def high_x(self):
        return self._high_x
        
    @high_x.setter
    def high_x(self, high_x):
        self._high_x = high_x
        self.bottom_right.x = high_x
        self.centre_right.x = high_x
        self.top_right.x    = high_x
        
        self.size.x = high_x - self._low_x
        self._set_centre_x(high_x - self.size.x // 2)
        
    @property
    def low_y(self):
        return self._low_y
        
    @low_y.setter
    def low_y(self, low_y):
        self._low_y = low_y
        self.bottom_right.y  = low_y
        self.bottom_centre.y = low_y
        self.bottom_left.y   = low_y
        
        self.size.y = self._high_y - low_y
        self._set_centre_y(low_y + self.size.y // 2)

    @property
    def high_y(self):
        return self._high_y
        
    @high_y.setter
    def high_y(self, high_y):
        self._high_y = high_y
        self.top_right.y  = high_y
        self.top_centre.y = high_y
        self.top_left.y   = high_y
        
        self.size.y = high_y - self._low_y
        self._set_centre_y(high_y - self.size.y // 2)
    
    @property
    def centre_x(self):
        return self._centre_x
    
    def _set_centre_x(self, centre_x):
        self._centre_x = centre_x
        self.top_centre.x = centre_x
        self.centre.x  = centre_x
        self.bottom_centre.x = centre_x
    
    @property
    def centre_y(self):
        return self._centre_y
    
    def _set_centre_y(self, centre_y):
        self._centre_y = centre_y
        self.centre_left.y = centre_y
        self.centre.y  = centre_y
        self.centre_right.y = centre_y
    
    
    def has_point(self, point: Vector):
        return (point.x >= self.low_x and point.x <= self.high_x
            and point.y >= self.low_y and point.y <= self.high_y)
    
    
    def intersects(self, other: Shape):
        if isinstance(other, RectangleShape):
            rect = other
            return (rect.low_x <= self.high_x and rect.high_x >= self.low_x
                and rect.low_y <= self.high_y and rect.high_y >= self.low_y)
        else:
            raise TypeError(
                f"Can't check intersection between {self} and {other}"
            )
    
    
    def __repr__(self):
        return (f"RectangleShape({self.low_x}, {self.low_y} -> "
              + f"{self.high_x}, {self.high_y})")
