from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from recordclass import RecordClass
from typing import Generic, TypeVar, NamedTuple, Union, Any
from itertools import islice

from adt import adt, Case

from lib import *
from card import *
from card.game import GameState, Rules
from .game import SjuanGameState
from .sjuan_card_stack import *
from .moves import *


class SjuanRules(Rules[
    SjuanAction, SjuanInsert, SjuanTake,
    SjuanGameState
]):
    @classmethod
    def reference(
        cls, move: Union[SjuanAction, SjuanTake, SjuanInsert],
        state: SjuanGameState
    ) -> Tuple[CardCollection, Any]:
        if type(move) == SjuanAction:
            pass
        elif type(move) == SjuanInsert:
            return move.match(
                sjuan_stack = lambda m: (state.sjuan_stack, m),
                player = lambda i, m: (state.players[i], m)
            )
        elif type(move) == SjuanTake:
            return move.match(
                src_stack = lambda m: (state.source_stack, m),
                player = lambda i, m: (state.players[i], m)
            )
        
        return None
    
    
    NUM_CARDS_TO_TAKE = 3
    
    class MoveInfo(RecordClass):
        is_valid:  bool
        ends_turn: bool
    def InvalidMove(**kwargs):
        return SjuanRules.MoveInfo(False, False, **kwargs)
    def ValidMove(**kwargs):
        return SjuanRules.MoveInfo(True, **kwargs)
    
    @classmethod
    def move_info(
        cls, moves: List[SjuanRules.Move], state: SjuanGameState
    ):
        def turn_info(turn_i):
            if len(moves) == 1:
                # Accept the player whose turn it is giving a card to the stack
                # or said player simply rearranging their own cards
                def from_to(take, insert):
                    take_valid = take.match(
                        src_stack = const(False),
                        player    = lambda i, _: i == turn_i
                    )
                    if take_valid:
                        return insert.match(
                            # Entering a card into the stack is always ok
                            sjuan_stack = const(
                                SjuanRules.ValidMove(ends_turn = True)
                            ),
                            player      = lambda i, _:
                                # Giving a card to a player is valid iff that
                                # player is us
                                SjuanRules.ValidMove(ends_turn = False)
                                if i == turn_i else SjuanRules.InvalidMove()
                        )
                    else:
                        return SjuanRules.InvalidMove()
                    
                return moves[0].match(
                    the_action = const(SjuanRules.InvalidMove()),
                    from_to    = from_to
                )
            elif len(moves) == cls.NUM_CARDS_TO_TAKE:
                # Accept the player whose turn it is ("us") taking
                # NUM_CARDS_TO_TAKE cards from the player right before them
                first_move_ok = moves[0].match(
                    the_action = const(False),
                    from_to    = lambda take, insert:
                        take.match(
                            src_stack = const(False),
                            player = lambda i, _:
                                # verify this player was right before us
                                state.incr_turn(i, 1) == turn_i
                        ) and insert.match(
                            sjuan_stack = const(False),
                            player = lambda i, _:
                                # verify the cards are being given to *us*
                                i == turn_i
                        )
                )
                
                all_3_moves_equal = all(move == moves[0] for move in moves[1:])
                
                return SjuanRules.MoveInfo(
                    is_valid  = first_move_ok and all_3_moves_equal,
                    ends_turn = True
                )
            else:
                return SjuanRules.InvalidMove()
        
        info = state.phase.match(
          do_queue = lambda _: SjuanRules.MoveInfo(
            is_valid  = deque(islice(state.queue, 0, len(moves))) == moves,
            ends_turn = len(state.queue) == len(moves)
          ),
          player_turn = lambda i: turn_info(i)
        )
        info.is_valid = info.is_valid and super().move_is_valid(moves, state)
        return info
    
    @classmethod
    def move_is_valid(
        cls, moves: List[SjuanRules.Move], state: SjuanGameState
    ) -> bool:
        return cls.move_info(moves, state).is_valid
    
    
    @classmethod
    def do(cls, moves: List[SjuanRules.Move], state: SjuanGameState) -> bool:
        info = cls.move_info(moves, state)
        if not info.is_valid:
            return False
        
        def do_moves(after_each = do_nothing, at_end = do_nothing):
            for move in list(moves):
                cls._do(move, state)
                after_each()
            
            at_end()
            if info.ends_turn:
                state.next_phase()
        
        def finish_turn():
            if info.ends_turn:
                i = state.turn_index()
                if len(state.players[i].cards) == 0:
                    # This player just won!
                    state.remove_player(i)
        
        state.phase.match(
            do_queue = lambda _: do_moves(
                after_each = state.queue.popleft
            ),
            player_turn = lambda _: do_moves(
                at_end = finish_turn
            )
        )
        
        return True
        
    
    @classmethod
    def suggested_moves(cls): pass

    @classmethod
    def moves_for_card(cls, i: int, state: SjuanGameState):
        curr_player_i = state.turn_index()
        curr_player   = state.players[curr_player_i]
        take_move = SjuanTake.PLAYER(curr_player_i, CardHandTake.HAND_TAKE(i))
        
        moves = []
        
        def add_move(insert):
            moves.append((
                SjuanRules.Move.FROM_TO(take_move, insert),
                take_move, insert
            ))
            
        for j in range(len(curr_player.cards)):
            if i != j:
                add_move(SjuanInsert.PLAYER(
                    curr_player_i, CardHandInsert.HAND_INSERT(j)
                ))
        
        card = curr_player.cards[i]
        move = SjuanCardStackInsert.SJUAN_INSERT()
        if state.sjuan_stack.insert_is_valid(move, card):
            add_move(SjuanInsert.SJUAN_STACK(move))
        
        return moves
