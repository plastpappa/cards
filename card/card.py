from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Generic, TypeVar


class CardColour(Enum):
    RED   = auto()
    BLACK = auto()
    
    def __str__(self):
        if self == CardColour.RED:
            return "Red"
        return "Black"


class CardSuit(Enum):
    HEARTS   = auto()
    SPADES   = auto()
    DIAMONDS = auto()
    CLUBS    = auto()
    
    @property
    def colour(self) -> CardColour:
        if self in (CardSuit.HEARTS, CardSuit.DIAMONDS):
            return CardColour.RED
        else:
            return CardColour.BLACK
    
    def _name(self, h: str, s: str, d: str, c: str) -> str:
        if self == CardSuit.HEARTS:
            return h
        if self == CardSuit.SPADES:
            return s
        if self == CardSuit.DIAMONDS:
            return d
        else:
            return c
    
    def name(self):
        return self._name("Hearts", "Spades", "Diamonds", "Clubs")
        
    def icon(self):
        return self._name("♥", "♠", "♦", "♣")
    
    def __str__(self):
        return self.icon()


class CardValue(Enum):
    TWO   = 2
    THREE = 3
    FOUR  = 4
    FIVE  = 5
    SIX   = 6
    SEVEN = 7
    EIGHT = 8
    NINE  = 9
    TEN   = 10
    JACK  = 11
    QUEEN = 12
    KING  = 13
    ACE   = 14
    
    def _name(self, j: str, q: str, k: str, a: str) -> str:
        if self.value <= 10:
            return str(self.value)
        elif self.value == 11:
            return j
        elif self.value == 11:
            return q
        elif self.value == 12:
            return k
        else:
            return a
    
    def __add__(self, n) -> str:
        return CardValue((self.value + n - 2) % 13 + 2)
    
    def name_short(self) -> str:
        return self._name("J", "Q", "K", "A")
        
    def name_long(self) -> str:
        return self._name("Jack", "Queen", "King", "Ace")
    
    def __str__(self):
        return self.name_short()


class Card:
    def __init__(self, suit: CardSuit, value: CardValue):
        self.suit  = suit
        self.value = value
    
    @property
    def colour(self) -> CardColour:
        return self.suit.colour
    
    def __str__(self):
        return f"{self.value} of {self.suit}"
    
    def __repr__(self):
        return f"Card({repr(self.suit)}, {repr(self.value)})"


# Collections of cards
NormalAction = TypeVar('NormalAction')
InsertAction = TypeVar('InsertAction')
TakeAction   = TypeVar('TakeAction')

CollectionState = TypeVar('CollectionState')

class CardCollection(ABC, Generic[
    NormalAction, InsertAction, TakeAction,
    CollectionState
]):
    @abstractmethod
    def action_is_valid(self, move: NormalAction) -> bool: pass
    @abstractmethod
    def do(self, move: NormalAction): pass
    
    @abstractmethod
    def insert_is_valid(self, move: InsertAction, card: Card) -> bool: pass
    @abstractmethod
    def do_insert(self, move: InsertAction, card: Card): pass
    
    @abstractmethod
    def take_is_valid(self, move: TakeAction) -> bool: pass
    @abstractmethod
    def do_take(self, move: TakeAction) -> List[Card]: pass
    
    @abstractmethod
    def get_state(self) -> CollectionState: pass
    @abstractmethod
    def set_state(self, state: CollectionState): pass
