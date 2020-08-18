from pyglet import shapes as shp, text as txt
from pyglet.graphics import Batch, OrderedGroup, NullGroup

from draw.vector import Vector
from draw.shape.rectangle import RectangleShape


class LabelWithBackground(txt.Label):
    def __init__(self, text = '', font_name = None, font_size = None,
                 bold = False, italic = False,
                 colour = (255, 255, 255, 255),
                 background_colour = (0, 0, 0, 128),
                 background_padding = Vector(6, 6),
                 pos = Vector(0, 0), size = Vector(None, None),
                 anchor_x = 'left', anchor_y = 'baseline',
                 align = 'left',
                 multiline = False, dpi = None, batch = None, group = None):
        self._group_bg   = OrderedGroup(0, group)
        self._group_text = OrderedGroup(1, group)
        
        super().__init__(text, font_name, font_size, bold, italic,
                         colour, pos.x, pos.y, size.x, size.y,
                         anchor_x, anchor_y, align, multiline,
                         dpi, batch, self._group_text)
        self._pos                = pos
        self._background_color   = background_colour
        self._background_padding = background_padding
        
        self.bg_draw = None
        self._update_bg()
        
    
    @property
    def pos(self):
        return self._pos
        
    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self.x, self.y = pos
        self._update_bg()
    
    @property
    def text_bounds(self):
        if self._multiline:
            width = self._width if self._wrap_lines else self.content_width
        else:
            width = self.content_width
            
        height = self.content_height if self._height is None else self._height
        
        left   = self._get_left()
        bottom = self._get_top(self._get_lines()) - height
        
        return RectangleShape(
            bottom_left = Vector(left, bottom),
            size        = Vector(width, height)
        )
        
    @property
    def bounds(self):
        text_bounds = self.text_bounds
        return RectangleShape(
            bottom_left = text_bounds.bottom_left - self._background_padding,
            size        = text_bounds.size + self._background_padding * 2
        )
    
    
    def _update_bg(self):
        if self.bg_draw:
            self.bg_draw.delete()
        
        bounds = self.bounds
        self.bg_draw = shp.Rectangle(
            bounds.low_x, bounds.low_y, bounds.size.x, bounds.size.y,
            color = self._background_color[0:3],
            batch = self._batch, group = self._group_bg
        )
        self.bg_draw.opacity = self._background_color[3]
        
        
    def delete(self):
        self.bg_draw.delete()
        super().delete()
