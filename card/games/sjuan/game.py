import math
from collections import deque
from typing import Any

from adt import adt, Case

from card import *
from card.game import Game
from .sjuan_card_stack import *
from .moves import *
from lib import const, do_nothing


NUM_CARDS_TO_TAKE = 3


@adt
class SjuanGameStatePhase:
    DO_QUEUE:    Case[Any]  # Really: Case[SjuanGameStatePhase]
    PLAYER_TURN: Case[int]
    GIVE_CARDS:  Case[int, int]
    
    def next(self, num_players):
        # Queue None -> Turn  0
        # Turn  n    -> Queue n
        # Queue n    -> Turn  n+1
        return self.match(
            do_queue    = lambda next_phase: next_phase,
            player_turn = lambda i: SjuanGameStatePhase.DO_QUEUE(
                SjuanGameStatePhase.PLAYER_TURN((i + 1) % num_players)
            ),
            give_cards  = lambda i, n:
                SjuanGameStatePhase.GIVE_CARDS(i, n - 1) if (n - 1) > 0
                else SjuanGameStatePhase.PLAYER_TURN(i + 1).next(num_players)
        )

class SjuanGameState:
    def __init__(self, num_players: int):
        self.queue = deque()
        self.phase = SjuanGameStatePhase.DO_QUEUE(
            SjuanGameStatePhase.PLAYER_TURN(0)
        )
        
        self.players = [
            CardHand([]) for i in range(num_players)
        ]
        self.sjuan_stack = SjuanCardStack()
        
        all_cards = [
            Card(suit, value) for suit  in CardSuit
                              for value in CardValue
        ]
        
        self.source_stack = CardStack(all_cards)
        self.source_stack.do(CardStackAction.STACK_SHUFFLE())
        
        for i, card in enumerate(all_cards):
            self.queue.append(SjuanRules.Move.FROM_TO(
                SjuanTake.SRC_STACK(CardStackTake.STACK_TAKE_TOP()),
                SjuanInsert.PLAYER(i % num_players, CardHandInsert.HAND_INSERT(0))
            ))
        
        self._on_turn_change        = []
        self._on_skippable_change   = []
        self._on_succumbable_change = []
        self._can_skip    = False
        self._can_succumb = True
    
    
    @property
    def can_skip(self):
        return self._can_skip
    
    @can_skip.setter
    def can_skip(self, can_skip):
        if can_skip != self._can_skip:
            self._can_skip = can_skip
            self.event(self._on_skippable_change, can_skip)
    
    @property
    def can_succumb(self):
        return self._can_succumb
    
    @can_succumb.setter
    def can_succumb(self, can_succumb):
        if can_succumb != self._can_succumb:
            self._can_succumb = can_succumb
            self.event(self._on_succumbable_change, can_succumb)
    
    def turn_incr(self, i: int, n: int):
        return (i + n) % len(self.players)
    
    def turn_index_(self, phase):
        return phase.match(
            do_queue    = lambda p:    self.turn_index_(p),
            player_turn = lambda i:    i,
            give_cards  = lambda i, _: i
        )
        
    def turn_index(self):
        return self.turn_index_(self.phase)
    
    
    def _turn_change(self, old_phase):
        self.can_skip    = False
        self.can_succumb = self.phase.match(
            do_queue    = const(False),
            player_turn = const(True),
            give_cards  = const(False)
        )
        self.event(self._on_turn_change, old_phase, self.phase, False)
        
    def next_phase(self):
        old_phase = deepcopy(self.phase)
        self.phase = self.phase.next(len(self.players))
        self._turn_change(old_phase)
        
    def ask_for_cards(self):
        old_phase = deepcopy(self.phase)
        i = self.turn_index()
        self.phase = SjuanGameStatePhase.DO_QUEUE(
            SjuanGameStatePhase.GIVE_CARDS(self.turn_incr(i, -1),
                                           NUM_CARDS_TO_TAKE)
        )
        self._turn_change(old_phase)
    
    def remove_player(self, i: int):
        self.players.pop(i)
        old_phase = deepcopy(self.phase)
        
        def adjusted_phase(phase):
            return self.phase.match(
                do_queue = lambda p:
                    SjuanGameStatePhase.DO_QUEUE(adjusted_phase(p)),
                player_turn = lambda j:
                    SjuanGameStatePhase.PLAYER_TURN(j - 1 if j > i else j),
                give_cards = lambda j:
                    SjuanGameStatePhase.GIVE_CARDS(j - 1 if j > i else j)
            )
        self.phase = adjusted_phase(self.phase)
            
        self._turn_change(old_phase)

        
    def listen(
        self,
        on_turn_change: Optional[Callable[
            [SjuanGameStatePhase, SjuanGameStatePhase, bool],
            None
        ]] = None,
        on_skippable_change: Optional[Callable[
            [bool], None
        ]] = None,
        on_succumbable_change: Optional[Callable[
            [bool], None
        ]] = None
    ):
        if on_turn_change:
            self._on_turn_change.append(on_turn_change)
        if on_skippable_change:
            self._on_skippable_change.append(on_skippable_change)
        if on_succumbable_change:
            self._on_succumbable_change.append(on_succumbable_change)
    
    def event(self, evt, *args, **kwargs):
        for f in evt:
            f(*args, **kwargs)

from .rules import SjuanRules

class SjuanGame(Game[SjuanGameState, SjuanRules]):
    def __init__(self, num_players: int):
        self.rules = SjuanRules
        self.state = SjuanGameState(num_players)
