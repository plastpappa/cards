from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from recordclass import RecordClass
from typing import Generic, TypeVar, NamedTuple, Union, Any, Optional, Callable
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
            return move.match(
                skip          = lambda: (None, None),
                ask_for_cards = lambda: (None, None)
            )
        elif type(move) == SjuanInsert:
            return move.match(
                sjuan_stack = lambda m:    (state.sjuan_stack, m),
                player      = lambda i, m: (state.players[i],  m)
            )
        elif type(move) == SjuanTake:
            i = state.turn_index()
            return move.match(
                src_stack = lambda m: (state.source_stack, m),
                myself = lambda m:
                    (None, None) if i is None
                    else (state.players[i], m)
            )

        return None


    NUM_CARDS_TO_TAKE = 3

    class MoveInfo(RecordClass):
        is_valid:      bool
        is_effectful:  bool = False
        ends_turn:     bool = False
        also_do:       Optional[Callable[[], None]] = None
        set_skippable: Optional[bool] = None
    def InvalidMove():
        return SjuanRules.MoveInfo(False, False, False, None)
    def ValidMove(**kwargs):
        return SjuanRules.MoveInfo(True, **kwargs)

    @classmethod
    def move_info(
        cls, moves: List[SjuanRules.Move], state: SjuanGameState
    ):
        def player_turn(turn_i):
            if len(moves) == 1:
                # Accept the player whose turn it is giving a card to the stack
                # or said player simply rearranging their own cards
                def from_to(take, insert):
                    take_valid = take.match(
                        src_stack = const(False),
                        myself    = const(True)
                    )
                    if take_valid:
                        ref_take, take_move = cls.reference(take, state)
                        cards = try_take(ref_take, take_move)
                        assert len(cards) == 1
                        card = cards[0]

                        return insert.match(
                            # Entering a card into the stack is always ok
                            sjuan_stack = const(
                                SjuanRules.ValidMove(
                                    ends_turn = (card.value not in [
                                        CardValue.ACE, CardValue.KING
                                    ]),
                                    is_effectful = True,
                                    # If our turn didn't end,
                                    # we should be able to skip
                                    # whatever remains
                                    set_skippable = True
                                )
                            ),
                            # Giving a card to a player is valid iff that
                            # player is us
                            player = lambda i, _:
                                SjuanRules.ValidMove(ends_turn = False)
                                if i == turn_i else SjuanRules.InvalidMove()
                        )
                    else:
                        return SjuanRules.InvalidMove()

                def the_action(action):
                    return action.match(
                        skip = const(
                            SjuanRules.ValidMove(ends_turn = True)
                            if state.can_skip else SjuanRules.InvalidMove()
                        ),
                        ask_for_cards = const(
                            SjuanRules.ValidMove(also_do = lambda:
                                state.ask_for_cards()
                            ) if state.can_succumb
                            else SjuanRules.InvalidMove()
                        )
                    )

                return moves[0].match(
                    the_action = the_action,
                    from_to    = from_to
                )
            else:
                return SjuanRules.InvalidMove()

        def give_cards(turn_i, n):
            if len(moves) == 1:
                move = moves[0]

                def to_next():
                    if n == 0:
                        return SjuanRules.InvalidMove()
                    else:
                        return SjuanRules.ValidMove(ends_turn = True)

                def to_self():
                    return SjuanRules.ValidMove(ends_turn = False)

                return move.match(
                    the_action = const(SjuanRules.InvalidMove()),
                    from_to    = lambda take, insert:
                        take.match(
                            src_stack = const(SjuanRules.InvalidMove()),
                            myself    = const(insert.match(
                                sjuan_stack = const(SjuanRules.InvalidMove()),
                                player = lambda i, _:
                                    to_next() if i == state.turn_incr(turn_i, 1)
                                    else (to_self() if i == turn_i
                                          else SjuanRules.InvalidMove())
                           ))
                       )
               )
            else:
                return SjuanRules.InvalidMove()

        info = state.phase.match(
          do_queue = lambda _: SjuanRules.MoveInfo(
            is_valid  = deque(islice(state.queue, 0, len(moves))) == moves,
            ends_turn = len(state.queue) == len(moves)
          ),
          player_turn = lambda i:    player_turn(i),
          give_cards  = lambda i, n: give_cards(i, n)
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

            if info.also_do is not None:
                info.also_do()
            at_end()
            if info.ends_turn:
                state.next_phase()
            elif info.set_skippable is not None:
                state.can_skip = info.set_skippable
            if info.is_effectful:
                state.can_succumb = False

        def finish_turn():
            i = state.turn_index()
            if i is not None and len(state.players[i].cards) == 0:
                # This player just won!
                state.player_won(i)

        state.phase.match(
            do_queue = lambda _: do_moves(
                after_each = state.queue.popleft, at_end = finish_turn
            ),
            player_turn = lambda _: do_moves(
                at_end = finish_turn
            ),
            give_cards = lambda _, __: do_moves(
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
        take_move     = SjuanTake.MYSELF(CardHandTake.HAND_TAKE(i))

        moves = []

        def add_move(insert):
            moves.append((
                SjuanRules.Move.FROM_TO(take_move, insert),
                take_move, insert
            ))

        for j in range(len(curr_player.cards)):
            # Inserts back into our own hand - always valid
            if i != j:
                add_move(SjuanInsert.PLAYER(
                    curr_player_i, CardHandInsert.HAND_INSERT(j)
                ))

            def player_turn():
                # Inserts into stack
                card = curr_player.cards[i]
                move = SjuanCardStackInsert.SJUAN_INSERT()
                if state.sjuan_stack.insert_is_valid(move, card):
                    add_move(SjuanInsert.SJUAN_STACK(move))

            def give_cards():
                # Inserts into next player's hands
                next_player_i = state.turn_incr(curr_player_i, 1)
                add_move(SjuanInsert.PLAYER(
                    next_player_i, CardHandInsert.HAND_INSERT(0)
                ))

            state.phase.match(
                do_queue    = do_nothing,
                player_turn = lambda _: player_turn(),
                give_cards  = lambda _, __: give_cards()
            )


        return moves
