from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Callable, List, Generic, TypeVar, Optional
from copy import deepcopy

from lib import do_nothing


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


    def adj_value(self, aces_lowest: bool = False):
        if aces_lowest and self == CardValue.ACE:
            return 1
        else:
            return self.value


    def _name(self, j: str, q: str, k: str, a: str) -> str:
        if self.value <= 10:
            return str(self.value)
        elif self.value == 11:
            return j
        elif self.value == 12:
            return q
        elif self.value == 13:
            return k
        else:
            return a

    def name_short(self) -> str:
        return self._name("J", "Q", "K", "A")

    def name_long(self) -> str:
        return self._name("Jack", "Queen", "King", "Ace")


    def __add__(self, n):
        return CardValue((self.value + n - 2) % 13 + 2)

    def __sub__(self, n):
        return self + (-n)

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

    def __eq__(self, other):
        try:
            return self.suit == other.suit and self.value == other.value
        except AttributeError:
            return False


# Collections of cards
NormalAction = TypeVar('NormalAction')
InsertAction = TypeVar('InsertAction')
TakeAction   = TypeVar('TakeAction')

CollectionState = TypeVar('CollectionState')

def try_take(ref, move):
    state0 = deepcopy(ref.get_state())
    if ref.take_is_valid(move):
        cards = ref._do_take(move)
        state1 = deepcopy(ref.get_state())
        ref.set_state(state0)
        return cards
    else:
        return None

class CardCollection(ABC, Generic[
    NormalAction, InsertAction, TakeAction,
    CollectionState
]):
    def __init__(self):
        self._listen_action = []
        self._listen_insert = []
        self._listen_take   = []

    @abstractmethod
    def action_is_valid(self, move: NormalAction) -> bool: pass
    @abstractmethod
    def _do(self, move: NormalAction): pass

    @abstractmethod
    def insert_is_valid(self, move: InsertAction, card: Card) -> bool: pass
    @abstractmethod
    def _do_insert(self, move: InsertAction, card: Card): pass

    @abstractmethod
    def take_is_valid(self, move: TakeAction) -> bool: pass
    @abstractmethod
    def _do_take(self, move: TakeAction) -> List[Card]: pass


    @abstractmethod
    def get_state(self) -> CollectionState: pass
    @abstractmethod
    def set_state(self, state: CollectionState): pass


    def do(self, move: NormalAction):
        res = self._do(move)
        self.event(self._listen_action, move)
        return res
    def do_insert(self, move: InsertAction, card: Card):
        res = self._do_insert(move, card)
        self.event(self._listen_insert, move, card)
        return res
    def do_take(self, move: TakeAction) -> List[Card]:
        res = self._do_take(move)
        self.event(self._listen_take, move)
        return res

    def listen(
        self,
        on_action: Optional[Callable[[NormalAction],       None]] = None,
        on_insert: Optional[Callable[[InsertAction, Card], None]] = None,
        on_take:   Optional[Callable[[TakeAction],         None]] = None
    ):
        if on_action:
            self._listen_action.append(on_action)
        if on_insert:
            self._listen_insert.append(on_insert)
        if on_take:
            self._listen_take.append(on_take)

    def event(self, evt, *args, **kwargs):
        for f in evt:
            f(*args, **kwargs)
