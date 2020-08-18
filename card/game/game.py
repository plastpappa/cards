from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type

from card import *


GameState = TypeVar('GameState')
Rules     = TypeVar('Rules')

class Game(ABC, Generic[GameState, Rules]):
    rules: Type[Rules]
    state: GameState
    
    @abstractmethod
    def suggested_moves(): pass
    
    @abstractmethod
    def moves_for_card(card: Card): pass
