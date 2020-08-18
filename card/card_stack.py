from typing import List, Optional
from random import shuffle

from adt import adt, Case

from card import Card, CardCollection


@adt
class CardStackAction:
    STACK_SHUFFLE: Case
    
@adt
class CardStackInsert:
    STACK_INSERT_BOTTOM: Case

@adt
class CardStackTake:
    STACK_TAKE_TOP: Case

class CardStack(CardCollection[
    CardStackAction, CardStackInsert, CardStackTake,
    List[Card]
]):
    def __init__(
        self, cards: List[Card],
        can_insert: bool = True, can_take: bool = True,
        allow_duplicates: bool = False
    ):
        self.cards = cards
        self.can_insert = can_insert
        self.can_take   = can_take
        self.allow_duplicates = allow_duplicates
    
    
    def action_is_valid(self, move: CardStackAction):
        return move.match(
            stack_shuffle = lambda: True
        )
    
    def do(self, move: CardStackAction):
        if self.action_is_valid(move):
            move.match(
                stack_shuffle = lambda:
                    shuffle(self.cards)
            )
    
    
    def insert_is_valid(self, move: CardStackInsert, card: Card) -> bool:
        return move.match(
            stack_insert_bottom = lambda: (
                self.can_insert and (self.allow_duplicates
                                  or card not in self.cards)
            )
        )
        
    def do_insert(self, move: CardStackInsert, card: Card):
        if self.insert_is_valid(move, card):
            move.match(
                stack_insert_bottom = lambda:
                    self.cards.append(card)
            )
    
    
    def take_is_valid(self, move: CardStackTake) -> bool:
        return move.match(
            stack_take_top = lambda: self.can_take
        )
    
    def do_take(self, move: CardStackTake) -> List[Card]:
        if self.take_is_valid(move):
            return move.match(
                stack_take_top = lambda: [ self.cards.pop(0) ]
            )
        else:
            return []
            
    
    def get_state(self):
        return self.cards
    
    def set_state(self, cards):
        self.cards = cards
