from typing import List, Dict

from adt import adt, Case

from card import Card, CardValue, CardSuit, CardCollection


@adt
class SjuanCardStackAction:
    pass

@adt
class SjuanCardStackInsert:
    SJUAN_INSERT: Case
    
    def __str__(self):
        return "insert"

@adt
class SjuanCardStackTake:
    pass



class SjuanCardStack(CardCollection[
    SjuanCardStackAction, SjuanCardStackInsert, SjuanCardStackTake,
    Dict[CardSuit, List[Card]]
]):
    def __init__(self):
        super().__init__()
        self.cards: Dict[CardSuit, List[Card]] = {}
    
    def action_is_valid(self, move): pass
    def _do(self, move): pass
    def take_is_valid(self, move): pass
    def _do_take(self, move): pass
        
        
    def insert_is_valid(self, move: SjuanCardStackInsert, card: Card) -> bool:
        try:
            row = self.cards[card.suit]
            lowest = row[0].value
            highest = row[-1].value
            return ((lowest  != CardValue.ACE  and card.value == lowest  - 1)
                 or (highest != CardValue.KING and card.value == highest + 1))
        except KeyError:
            return card.value == CardValue.SEVEN
    
    def _do_insert(self, move: SjuanCardStackInsert, card: Card):
        try:
            row = self.cards[card.suit]
            if row[0].value - 1 == card.value:
                row.insert(0, card)
            elif row[-1].value + 1 == card.value:
                row.append(card)
        except KeyError:
            if card.value == CardValue.SEVEN:
                self.cards[card.suit] = [card]
    
    
    def get_state(self):
        return self.cards
    
    def set_state(self, cards):
        self.cards = cards
