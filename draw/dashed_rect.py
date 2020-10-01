from typing import List

from pyglet.graphics import Batch

from draw.shape import RectangleShape
from draw.rect_outline import RectOutline


class DashedRect:
    def __init__(
        self, shape: RectangleShape, dashes: List[int],
        colour = (255, 255, 255, 255), stroke_width: int = 2,
        batch = None, group = None
    ):
        self._shape        = shape
        self._dashes       = dashes
        self._colour       = colour
        self._stroke_width = stroke_width
        if len(self._dashes) % 2 == 1:
            self._dashes.extend(self._dashes)
        
        if batch is None:
            self._batch = Batch()
            self._batch_is_own = True
        else:
            self._batch = batch
            self._batch_is_own = False
        self._group = group
        
        self._x = RectOutline(
            shape, colour = self._colour, stroke_width = self._stroke_width,
            batch = self._batch, group = self._group
        )
        
    
    @property
    def shape(self):
        return self._shape
    
    
    def draw(self):
        if self._batch_is_own:
            self._batch.draw()
        else:
            self._x.draw()
            
    def delete(self):
        self._x.delete()
