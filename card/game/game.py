from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar, Type

from card import *


GameState = TypeVar('GameState')
Rules     = TypeVar('Rules')

class Game(ABC, Generic[GameState, Rules]):
    rules: Type[Rules]
    state: GameState

    def __init__(self):
        self._on_move = []

    def do(self, moves):
        old_state_state = deepcopy(self.state.get_state())
        res = self.rules.do(moves, self.state)
        if res:
            old_state = self.state.__class__.from_state(old_state_state)
            for f in self._on_move:
                f(moves, old_state)
        return res

    def is_valid(self, moves):
        return self.rules.move_is_valid(moves, self.state)

    def moves_for_card(self, i: int):
        return self.rules.moves_for_card(i, self.state)

    def listen(self,
        on_move = None
    ):
        if on_move is not None:
            self._on_move.append(on_move)
