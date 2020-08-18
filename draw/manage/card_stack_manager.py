from card import *
from draw.draw import *
from draw.vector import Vector
from draw.manage import World


class CardStackManager:
    def __init__(
        self, stack: CardStack, pos: Vector, label: str,
        interactable: bool = True
    ):
        self._stack  = stack
        self._drawer = CardStackDrawer(stack.cards, pos, label)
        self._interactable = interactable
        
    
    def draw(self):
        self._drawer.draw()
    
    def mouse_at(self, mouse_pos, delta, button, modifiers):
        if self._interactable and self._stack.can_take:
            self._drawer._card_draw.targeted = (
                self._drawer._card_draw.has_point(mouse_pos))
    
    def mouse_down(self, mouse_pos, button, modifiers):
        pass   # todo
