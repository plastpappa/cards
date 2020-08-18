from pyglet import shapes as shp


class RectOutline:
    def __init__(self, x, y, width, height, stroke_width = 1, color = (255, 255, 255), **kwargs):
        self.lines = [
            shp.Line( x,         y,               x,         y + height,      stroke_width, color, **kwargs),
            shp.Line( x,         y + height,      x + width, y + height,      stroke_width, color, **kwargs),
            shp.Line( x + width, y + height,      x + width, y,               stroke_width, color, **kwargs),
            shp.Line( x + width, y,               x,         y,               stroke_width, color, **kwargs)
        ]

    def draw(self):
        for line in self.lines:
            line.draw()
            
    def delete(self):
        for line in self.lines:
            line.delete()
