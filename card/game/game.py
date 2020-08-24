from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type

from card import *


GameState = TypeVar('GameState')
Rules     = TypeVar('Rules')

class Game(ABC, Generic[GameState, Rules]):
    rules: Type[Rules]
    state: GameState
