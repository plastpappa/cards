from draw.bg_label import *
from draw.rect_outline import *
from pyglet.graphics import Batch, OrderedGroup
from lib import do_nothing


class ButtonManager:
    def __init__(
        self, label: str, bounds: RectangleShape,
        on_click = do_nothing,
        stroke_width: int = 2,
        font_name: str = "Source Code Pro", font_size: int = 12,
        text_colour         = (255, 255, 255, 255),
        background_colour   = (255, 0,   0,   255),
        background_colour_2 = (255, 0,   0,   255),
        outline_colour      = (0,   255, 255, 255),
        batch = None, group = None
    ):
        self._label  = label
        self._bounds = bounds
        self._on_click = on_click
        self._stroke_width = stroke_width
        self._font_name    = font_name
        self._font_size    = font_size
        self._text_colour         = text_colour
        self._background_colour   = background_colour
        self._background_colour_2 = background_colour_2
        self._outline_colour      = outline_colour
        
        if batch is None:
            self._batch = Batch()
            self._batch_is_own = True
        else:
            self._batch = batch
            self._batch_is_own = False
        self._group_back  = OrderedGroup(0, group)
        self._group_front = OrderedGroup(1, group)
        
        self._text_and_bg = None
        self._outline     = None
        self._update()
    
    
    @property
    def label(self):
        return self._label
        
    @label.setter
    def label(self, label):
        if self._label != label:
            self._label = label
            self._update()
    
    
    def _update_text_and_bg(self):
        self._delete_text_and_bg()
        self._text_and_bg = LabelWithBackground(
            self._label,
            font_name = self._font_name, font_size = self._font_size,
            colour = self._text_colour,
            background_colour = self._background_colour,
            background_padding = Vector(0, 0),
            background_bounds = self._bounds,
            pos = self._bounds.centre,
            anchor_x = 'center', anchor_y = 'center',
            batch = self._batch, group = self._group_back
        )
    
    def _update_outline(self):
        self._delete_outline()
        self._outline = RectOutline(
            self._bounds, self._stroke_width, self._outline_colour,
            batch = self._batch, group = self._group_front
        )
        
    def _update(self):
        self._update_text_and_bg()
        self._update_outline()
            
    
    def _delete_text_and_bg(self):
        if self._text_and_bg:
            self._text_and_bg.delete()
            self._text_and_bg = None
    
    def _delete_outline(self):
        if self._outline:
            self._outline.delete()
            self._outline = None
    
    def delete(self):
        self._delete_text_and_bg()
        
        
    def draw(self):
        if self._batch_is_own:
            self._batch.draw()
        else:
            self._text_and_bg.draw()
            self._outline.draw()
            
    def mouse_at(self, mouse_pos, delta, button, modifiers):
        if self._bounds.has_point(mouse_pos):
            self._text_and_bg.bg_draw.color   = self._background_colour_2[0:3]
            self._text_and_bg.bg_draw.opacity = self._background_colour_2[3]
        else:
            self._text_and_bg.bg_draw.color   = self._background_colour[0:3]
            self._text_and_bg.bg_draw.opacity = self._background_colour[3]
            
    def mouse_down(self, mouse_pos, button, modifiers):
        if self._bounds.has_point(mouse_pos):
            self._on_click()
