from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union
from copy import deepcopy

from adt import adt, Case

from card import *
from .game import GameState


Action = TypeVar('Action')
Insert = TypeVar('Insert')
Take   = TypeVar('Take')

class Rules(ABC, Generic[Action, Insert, Take, GameState]):
    @adt
    class Move:
        THE_ACTION: Case[Action]
        FROM_TO: Case[Take, Insert]
    
    
    @classmethod
    @abstractmethod
    def reference(
        cls, move: Union[Action, Take, Insert], state: GameState
    ) -> CardCollection:
        pass
    
    
    @classmethod
    def move_is_valid(cls, moves: List[Move], state: GameState) -> bool:
        def from_to_valid(take, insert):
            ref_take, take_move = cls.reference(take, state)
            state0 = deepcopy(ref_take.get_state())
            if ref_take.take_is_valid(take_move):
                cards = ref_take.do_take(take_move)
                ref_take.set_state(state0)
                
                ref_insert, insert_move = cls.reference(insert, state)
                return all(
                    ref_insert.insert_is_valid(insert_move, card)
                    for card in cards
                )
            else:
                return False
        
        def action_valid(action):
            ref_action, action_move = cls.reference(action)
            return ref_action.action_is_valid(action_move)
            
        return all(
            move.match(
                the_action = action_valid,
                from_to = from_to_valid
            )
            for move in moves
        )

    @classmethod
    def _do(cls, move: Move, state: GameState):
        def from_to(take, insert):
            take_ref, take_move = cls.reference(take, state)
            cards = take_ref.do_take(take_move)
            for card in cards:
                insert_ref, insert_move = cls.reference(insert, state)
                insert_ref.do_insert(insert_move, card)
        
        def the_action(action):
            action_ref, action_move = cls.reference(action, state)
            action_ref.do(action_move)
        
        move.match(
            the_action = the_action,
            from_to = from_to
        )
    
    
    @classmethod
    @abstractmethod
    def do(cls, move: Move, state: GameState) -> bool:
        pass
