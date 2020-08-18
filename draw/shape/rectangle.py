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
        
        self.top_right               = self.bottom_left + self.size
        self.low_x,    self.low_y    = self.bottom_left
        self.centre_x, self.centre_y = self.centre
        self.high_x,   self.high_y   = self.top_right
        
        self.centre_left   = Vector(self.low_x,    self.centre_y)
        self.top_left      = Vector(self.low_x,    self.high_y)
        self.bottom_right  = Vector(self.high_x,   self.low_y)
        self.centre_right  = Vector(self.high_x,   self.centre_y)
        self.top_centre    = Vector(self.centre_x, self.high_y)
        self.bottom_centre = Vector(self.centre_x, self.low_y)
        
        
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
