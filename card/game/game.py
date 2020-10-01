from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type

from card import *


GameState = TypeVar('GameState')
Rules     = TypeVar('Rules')

class Game(ABC, Generic[GameState, Rules]):
    rules: Type[Rules]
    state: GameState
    
    def do(self, moves):
        return self.rules.do(moves, self.state)
        
    def moves_for_card(self, i: int):
        return self.rules.moves_for_card(i, self.state)
