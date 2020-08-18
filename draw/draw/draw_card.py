import math
from operator import attrgetter as attr

from pyglet import shapes as shp, text as txt, image as img, sprite, font
from pyglet.graphics import OrderedGroup, Batch
from pyglet.gl import *

from international import IMG_DIR
from card import *
from draw.rect_outline import *
from draw.round_rect import *
from draw.vector import *
from draw.shape import RectangleShape


def update_sym_label_position(labels, dir: int, pos: Vector):
    icon_label, value_label = labels
    
    
class CardDrawer(RectangleShape):
    CARD_SIZE    = Vector(42, 60)
    PADDING      = Vector(3, 0)
    BACK_PADDING = 4
    
    TRANSPARENT_OPACITY     = 100
    OUTLINE_COLOUR_TARGETED = (220, 145, 53)
    OUTLINE_COLOUR_NORMAL   = (180, 180, 180)
    RED_COLOUR              = (250, 72, 72)
    BLACK_COLOUR            = (20, 20, 33)
    
    # Centered at pos
    def __init__(
        self, card: Card, pos: Vector,
        transparent: bool = False, targeted: bool = False,
        hidden: bool = False,
        batch = None, group = None
    ):
        super().__init__(centre = pos, size = CardDrawer.CARD_SIZE)
        
        self.card   = card
        self.anchor = pos
        self._transparent = transparent
        self._targeted    = targeted
        self._hidden      = hidden
        self.batch       = batch
        self.group_back  = OrderedGroup(0, group)
        self.group_front = OrderedGroup(1, group)
        
        self.image = img.load(IMG_DIR.joinpath('card.jpg'))
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        
        self.rect              = None
        self.outline           = None
        self.sym_labels_top    = []
        self.sym_labels_bottom = []
        self.num_label         = None
        self.back              = None
        self._update()
    
    
    @property
    def pos(self):
        return self.centre
        
    @pos.setter
    def pos(self, pos):
        super().__init__(centre = pos, size = CardDrawer.CARD_SIZE)
        
        self._delete_common()
        self._update_common()
        if self._hidden:
            self._delete_back()
            self._update_hidden()
        else:
            self._adjust_sym_labels()
            self.num_label.x, self.num_label.y = pos
        
    
    @property
    def transparent(self):
        return self._transparent
        
    @transparent.setter
    def transparent(self, transparent: bool):
        if transparent != self._transparent:
            self._transparent = transparent
            self.redraw()
        
    @property
    def targeted(self):
        return self._targeted
        
    @targeted.setter
    def targeted(self, targeted: bool):
        if targeted != self._targeted:
            self._targeted = targeted
            if self.outline is not None:
                self.outline.delete()
            self._update_outline()
    
    @property
    def hidden(self):
        return self._hidden
        
    @hidden.setter
    def hidden(self, hidden: bool):
        if hidden and not self._hidden:
            self._hidden = True
            self._delete_front()
            self._update_hidden()
        elif not hidden and self._hidden:
            self._hidden = False
            self._delete_back()
            self._update_visible()
    
    @property
    def opacity(self):
        return CardDrawer.TRANSPARENT_OPACITY if self.transparent else 255
    
    
    def _update(self):
        self._update_common()
        
        if self.hidden:
            self._update_hidden()
        else:
            self._update_visible()
    
    def _update_common(self):
        self.rect = shp.Rectangle(
            *self.bottom_left, *self.size,
            color = (255, 255, 255),
            batch = self.batch, group = self.group_back
        )
        self.rect.opacity = self.opacity
        self._update_outline()
    
    def _update_outline(self):
        colour  = (CardDrawer.OUTLINE_COLOUR_TARGETED if self.targeted
                   else CardDrawer.OUTLINE_COLOUR_NORMAL)
        
        self.outline = RectOutline(
            *self.bottom_left, *self.size,
            color = colour, stroke_width = 2,
            batch = self.batch, group = self.group_back
        )
        self.outline.opacity = self.opacity
            
    def _update_hidden(self):
        self.back = sprite.Sprite(
            self.image, *self.centre,
            batch = self.batch, group = self.group_front
        )
        self.back.opacity = self.opacity
        self.back.scale = ((self.size.y - 2 * CardDrawer.BACK_PADDING)
                          / self.image.height)
    
    def _sym_label_part_positions(self, place: int, pos: Vector):
        return [
            Vector(x + place * pad.x,
                   y - place * pad.y),
            Vector(x + place * pad.x,
                   y - place * 0.9 * icon_label.document.get_font().ascent)
        ]
    
    def _adjust_sym_labels(self):
        def adjust_mini(icon_label, value_label, place: int, pos: Vector):
            smaller = min(icon_label, value_label, key = attr('content_width'))
            if smaller is icon_label:
                larger = value_label
            else:
                larger = icon_label
            
            larger.x = pos.x + place * CardDrawer.PADDING.x
            larger.anchor_x = 'left' if place == 1 else 'right'
            smaller.x = larger.x + place * larger.content_width // 2
            smaller.anchor_x = 'center'
            
            icon_label.y  = pos.y + place * CardDrawer.PADDING.y
            value_label.y = pos.y - (icon_label.document.get_font().ascent
                            * place * (0.9 if place == 1 else 0.8))
        
        adjust_mini(self.sym_labels_top[0], self.sym_labels_top[1],
                    1, self.top_left)
        adjust_mini(self.sym_labels_bottom[0], self.sym_labels_bottom[1],
                    -1, self.bottom_right + Vector(0, 3))
    
    def _update_visible(self):
        pad = CardDrawer.PADDING
        
        colour_ = (CardDrawer.RED_COLOUR if self.card.colour == CardColour.RED
                   else CardDrawer.BLACK_COLOUR)
        colour = (*colour_, self.opacity)
        
        def make_sym_labels(anchor_y: str):
            icon_label = txt.Label(
                self.card.suit.icon(),
                color = colour,
                font_name = 'Source Code Pro', font_size = 9,
                anchor_y = anchor_y,
                batch = self.batch, group = self.group_front
            )
            value_label = txt.Label(
                str(self.card.value),
                color = colour,
                font_name = 'Source Code Pro',
                font_size = 6 if self.card.value == CardValue.TEN else 8,
                anchor_y = anchor_y,
                batch = self.batch, group = self.group_front
            )
                        
            return (icon_label, value_label)
        
        self.sym_labels_top    = make_sym_labels('top')
        self.sym_labels_bottom = make_sym_labels('baseline')
        self._adjust_sym_labels()
        
        self.num_label = txt.Label(
            str(self.card.value),
            color = colour,
            x = self.centre.x,
            y = self.centre.y,
            anchor_x = 'center', anchor_y = 'center',
            font_name = 'Source Code Pro', bold = True, font_size = 13,
            batch = self.batch, group = self.group_front
        )
        
    
    def delete(self):
        self._delete_common()
        self._delete_front()
        self._delete_back()
    
    def _delete_common(self):
        if self.rect:
            self.rect.delete()
            self.rect = None
        self._delete_outline()
    
    def _delete_outline(self):
        if self.outline:
            self.outline.delete()
            self.outline = None
            
    def _delete_front(self):
        for label in self.sym_labels_top + self.sym_labels_bottom:
            label.delete()
        self.sym_labels_top = []
        self.sym_labels_bottom = []
        if self.num_label:
            self.num_label.delete()
            self.num_label = None
            
    def _delete_back(self):
        if self.back:
            self.back.delete()
            self.back = None
    
    def redraw(self):
        self.delete()
        self._update()
        
        
    def draw(self, rotation: int = 0):
        glPushMatrix()
        glTranslatef(self.anchor.x, self.anchor.y, 0)
        glRotatef(rotation, 0.0, 0.0, 1.0)
        glTranslatef(-self.anchor.x, -self.anchor.y, 0)
        
        self.rect.draw()
        self.outline.draw()
        for label in self.sym_labels:
            label.draw()
        if self.num_label:
            self.num_label.draw()
        else:
            self.back.draw()
        
        glPopMatrix()
