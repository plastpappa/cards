from pyglet import shapes as shp

from draw.shape import RectangleShape


class RectOutline:
    def __init__(
        self, shape: RectangleShape,
        stroke_width = 1, colour = (255, 255, 255, 255),
        **kwargs
    ):
        a   = shape.bottom_left
        b   = shape.top_right
        rgb = colour[0:3]
        op  = colour[3]
        
        self._lines = [
            shp.Line(a.x, a.y, a.x, b.y, stroke_width, rgb, **kwargs),
            shp.Line(a.x, b.y, b.x, b.y, stroke_width, rgb, **kwargs),
            shp.Line(b.x, b.y, b.x, a.y, stroke_width, rgb, **kwargs),
            shp.Line(b.x, a.y, a.x, a.y, stroke_width, rgb, **kwargs)
        ]
        for line in self._lines:
            line.opacity = op
    
            
    def delete(self):
        for line in self._lines:
            line.delete()
            
            
    def draw(self):
        for line in self._lines:
            line.draw()
