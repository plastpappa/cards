from typing import List, Optional

from adt import adt, Case

from card import Card, CardCollection


@adt
class CardHandAction:
    pass

@adt
class CardHandInsert:
    HAND_INSERT: Case[int]

@adt
class CardHandTake:
    HAND_TAKE: Case[int]

class CardHand(CardCollection[
    CardHandAction, CardHandInsert, CardHandTake,
    List[Card]
]):
    def __init__(
        self, cards: List[Card],
        allow_duplicates: bool = False,
        min_cards: Optional[int] = None,
        max_cards: Optional[int] = None
    ):
        self.cards = cards
        self.allow_duplicates = allow_duplicates
        self.min_cards = min_cards
        self.max_cards = max_cards
    

    def action_is_valid(self, move: CardHandAction):
        return True
    
    def do(self, move: CardHandAction):
        pass
            
                
    def insert_is_valid(self, move: CardHandInsert, card: Card) -> bool:
        return move.match(
            hand_insert = lambda i:
                i >= 0 and i <= len(self.cards)
                and (self.allow_duplicates or card not in self.cards)
                and (self.max_cards is None
                     or len(self.cards) <= self.max_cards - 1)
        )
        
    def do_insert(self, move: CardHandInsert, card: Card):
        if self.insert_is_valid(move, card):
            move.match(
                hand_insert = lambda i:
                    self.cards.insert(i, card)
            )
    
    
    def take_is_valid(self, move: CardHandTake) -> bool:
        return move.match(
            hand_remove = lambda i:
                i >= 0 and i < len(self.cards)
                and (self.min_cards is None
                     or len(self.cards) >= self.min_cards + 1)
        )
            
    def do_take(self, move: CardHandTake) -> List[Card]:
        if self.take_is_valid(self, move):
            return move.match(
                hand_remove = lambda i: [ self.cards.pop(i) ]
            )
        else:
            return []
            
    
    def get_state(self) -> List[Card]:
        return self.cards
    
    def set_state(self, cards: List[Card]):
        self.cards = cards
