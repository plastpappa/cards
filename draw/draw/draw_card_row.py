from copy import deepcopy
from itertools import islice

from pyglet import shapes as shp, text as txt, font
from pyglet.graphics import Batch

from card import *
from draw.draw import *
from draw.vector import *
from draw.bg_label import *


class CardRowDrawer:
    CARD_PADDING     = Vector(6, 0)
    LABEL_HOVER      = Vector(0, 18)
    ETC_PADDING      = Vector(16, 0)
    TEXT_COLOUR      = (255, 255, 255, 170)
    LABEL_BG_COLOUR  = (160, 188, 255, 120)
    LABEL_BG_PADDING = Vector(12, 1)
    
    # Centered at pos
    def __init__(
        self, cards: List[Card],
        pos: Vector, rotation: int = 0,
        label: str = None,
        row_size: int = 10,
        hidden: bool = False,
        batch = None, group = None
    ):
        self._pos      = pos
        self._anchor   = pos
        self.rotation  = rotation
        self._cards    = cards
        self._label    = label
        self._row_size = row_size
        self._offset   = 0
        
        if batch is None:
            self._batch = Batch()
            self._batch_is_own = True
        else:
            self._batch = batch
            self._batch_is_own = False
        self._group = group
        
        self._card_draws   = []
        self._top_labels   = []
        self._etc_left     = None
        self._etc_right    = None
        self._n_displayed  = None
        self._bounds_inner = None
        self._update_displayed_cards()
        self._update_cards()
        self._update_top_labels()
        if len(self._cards) > self._row_size:
            self._add_etc_right()
        self.hidden = hidden
    
    
    @property
    def hidden(self):
        return self._hidden
        
    @hidden.setter
    def hidden(self, hidden):
        self._hidden = hidden
        for card_draw in self._card_draws:
            card_draw.hidden = hidden
        
    @property
    def pos(self):
        return self._pos
        
    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self._bounds_inner = self.bounds_inner
        self._update_displayed_cards()
        self._update_card_positions()
        self._update_label_positions()
        if self._etc_left:
            self._delete_etc_left()
            self._add_etc_left()
        if self._etc_right:
            self._delete_etc_right()
            self._add_etc_right()
    
    @property
    def label(self):
        return self._label
        
    @label.setter
    def label(self, label):
        self._label = label
        self._update_top_labels()
        
    @property
    def max_offset(self):
        return max(0, len(self._cards) - self._row_size)
        
    @property
    def offset(self):
        return self._offset
        
    @offset.setter
    def offset(self, offset):
        if self._offset == offset:
            return
        
        bound_right = self.max_offset
        if offset < 0 or offset > bound_right:
            raise ValueError(f'Must have 0 <= offset <= {bound_right}, '
                           + f'got {offset}.')
            
        old_offset = self._offset
        self._offset = offset
        self._update_displayed_cards()
                
        if self._offset > 0:
            if old_offset == 0:
                self._add_etc_left()
        else:
            self._delete_etc_left()
        
        if self._offset < bound_right:
            if old_offset == bound_right:
                self._add_etc_right()
        else:
            self._delete_etc_right()
            
        self._update_displayed_cards()

    
    def incr_offset(self):
        if self._offset == self.max_offset:
            return
        if self._offset == 0:
            self._add_etc_left()
            
        self._offset += 1
        if self._offset == self.max_offset:
            self._delete_etc_right()
        
        tail = self._card_draws[1:]
        pos_last = tail[-1].pos.copy()
        for card_draw in tail:
            card_draw.pos -= Vector(self.delta().x, 0)
        self._card_draws[0].delete()
        self._card_draws = [
            *tail,
            CardDrawer(self._cards[self._offset + self._row_size - 1],
                       pos_last, batch = self._batch, group = self._group)
        ]
    
    def decr_offset(self):
        if self._offset == 0:
            return
        if self._offset == self.max_offset:
            self._add_etc_right()
            
        self._offset -= 1
        if self._offset == 0:
            self._delete_etc_left()
        
        init = self._card_draws[:-1]
        pos_first = self._card_draws[0].pos.copy()
        for card_draw in init:
            card_draw.pos += Vector(self.delta().x, 0)
        self._card_draws[-1].delete()
        self._card_draws = [
            CardDrawer(self._cards[self._offset], pos_first,
                       batch = self._batch, group = self._group),
            *init
        ]
    
    
    def delta(self, last = False):
        return (CardDrawer.CARD_SIZE
              + (Vector(0, 0) if last else CardRowDrawer.CARD_PADDING))
    
    @property
    def n_displayed(self):
        return min(len(self._cards) - self._offset, self._row_size)
    
    @property
    def bounds_inner(self):
        size = Vector(
            (self._n_displayed - 1) * self.delta().x + self.delta(True).x,
            self.delta(True).y
        )
        return RectangleShape(centre = self._pos, size = size)
        
    @property
    def cards_start_pos(self):
        return self.bounds_inner.bottom_left + CardDrawer.CARD_SIZE // 2
    
    
    def _update_displayed_cards(self):
        new_n_displayed = self.n_displayed
        if new_n_displayed != self._n_displayed:
            self._n_displayed  = new_n_displayed
        self._bounds_inner = self.bounds_inner
    
    def _update_cards(self):
        self._delete_cards()
        
        for i in range(self.n_displayed):
            card = self._cards[self._offset + i]
            self._card_draws.append(CardDrawer(
                card, Vector(0, 0), batch = self._batch, group = self._group
            ))
            
        self._update_card_positions()
        
    def _update_card_positions(self):
        pos = self.cards_start_pos.copy()
        for card in self._card_draws:
            card.pos = pos
            pos += Vector(self.delta().x, 0)
    
    def _update_top_labels(self):
        self._delete_top_labels()
        
        info = LabelWithBackground(
            f"{len(self._cards)} kort",
            colour = CardRowDrawer.TEXT_COLOUR,
            background_colour = CardRowDrawer.LABEL_BG_COLOUR,
            background_padding = CardRowDrawer.LABEL_BG_PADDING,
            pos = Vector(0, 0),
            anchor_x = 'center', anchor_y = 'bottom',
            font_name = 'Source Code Pro', font_size = 10,
            batch = self._batch, group = self._group
        )
        
        name = LabelWithBackground(
            self._label,
            colour = CardRowDrawer.TEXT_COLOUR,
            background_colour = CardRowDrawer.LABEL_BG_COLOUR,
            background_padding = CardRowDrawer.LABEL_BG_PADDING,
            pos = Vector(0, 0),
            anchor_x = 'center', anchor_y = 'bottom',
            font_name = 'Source Code Pro', font_size = 10,
            batch = self._batch, group = self._group
        )
        
        self._top_labels = [info, name]
        self._update_label_positions()
        
    def _update_label_positions(self):
        info, name = self._top_labels
        info.pos = self._bounds_inner.top_centre + CardRowDrawer.LABEL_HOVER
        name.pos = info.bounds.top_centre + Vector(0, 7)
    
    def _add_etc_left(self):
        pos = self._bounds_inner.centre_left - CardRowDrawer.ETC_PADDING
        self._etc_left = txt.Label(
            "<<", color = (230, 230, 230, 255),
            x = pos.x, y = pos.y,
            anchor_x = 'right', anchor_y = 'center',
            font_name = 'Source Code Pro', font_size = 16,
            batch = self._batch, group = self._group
        )
        
    def _add_etc_right(self):
        pos = self._bounds_inner.centre_right + CardRowDrawer.ETC_PADDING
        self._etc_right = txt.Label(
            ">>", color = (230, 230, 230, 255),
            x = pos.x, y = pos.y,
            anchor_x = 'left', anchor_y = 'center',
            font_name = 'Source Code Pro', bold = True, font_size = 16,
            batch = self._batch, group = self._group
        )
    
    
    def _delete_cards(self):
        for draw in self._card_draws:
            draw.delete()
        self._card_draws = []
        
    def _delete_top_labels(self):
        for draw in self._top_labels:
            draw.delete()
        self._top_labels = []
    
    def _delete_etc_left(self):
        if self._etc_left:
            self._etc_left.delete()
            self._etc_left = None
            
    def _delete_etc_right(self):
        if self._etc_right:
            self._etc_right.delete()
            self._etc_right = None
    
    def delete(self):
        self._delete_cards()
        self._delete_top_labels()
        self._delete_etc_left()
        self._delete_etc_right()
    
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self._pos.x, self._pos.y, 0)
        glRotatef(self.rotation, 0.0, 0.0, 1.0)
        glTranslatef(-self._pos.x, -self._pos.y, 0)
        
        if self._batch_is_own:
            self._batch.draw()
        else:
            for card in self._card_draws + self._top_labels:
                card.draw()
            if self._etc_left:
                self._etc_left.draw()
            if self._etc_right:
                self._etc_right.draw()
                
        glPopMatrix()
