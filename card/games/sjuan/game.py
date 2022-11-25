import random
from collections import deque
from typing import Any
from copy import deepcopy

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
    def __init__(self, cards, num_players: int, can_always_skip: bool = True):
        self._cards           = cards
        self._num_players     = num_players
        self._can_always_skip = can_always_skip

        self._on_turn_change        = []
        self._on_skippable_change   = []
        self._on_succumbable_change = []
        self._on_win                = []

        self.reset()

    def reset(self):
        self.queue = deque()

        first_player = random.randint(0, self._num_players - 1)
        self.phase = SjuanGameStatePhase.DO_QUEUE(
            SjuanGameStatePhase.PLAYER_TURN(first_player)
        )

        self.players = [
            CardHand([]) for i in range(self._num_players)
        ]
        self.sjuan_stack = SjuanCardStack()

        all_cards = deepcopy(self._cards)
        self.source_stack = CardStack(all_cards)
        self.source_stack.do(CardStackAction.STACK_SHUFFLE())

        for i, card in enumerate(all_cards):
            self.queue.append(SjuanRules.Move.FROM_TO(
                SjuanTake.SRC_STACK(CardStackTake.STACK_TAKE_TOP()),
                SjuanInsert.PLAYER(i % self._num_players, CardHandInsert.HAND_INSERT(0))
            ))

        self._can_skip    = None
        self._can_succumb = True


    def get_state(self):
        return { 'cards': self._cards, 'num_players': self._num_players, 'can_always_skip': self._can_always_skip,
                 'queue': self.queue, 'phase': self.phase,
                 'players': [ player.get_state() for player in self.players ],
                 'sjuan_stack': self.sjuan_stack.get_state(),
                 'source_stack': self.source_stack.get_state(),
                 'can_skip': self._can_skip, 'can_succumb': self._can_succumb }

    @classmethod
    def from_state(cls, state):
        me = SjuanGameState(state['cards'], state['num_players'], state['can_always_skip'])
        me.queue = state['queue']
        me.phase = state['phase']
        for i, player in enumerate(me.players):
            player.set_state(state['players'][i])
        me.sjuan_stack.set_state(state['sjuan_stack'])
        me.source_stack.set_state(state['source_stack'])
        me._can_skip = state['can_skip']
        me._can_succumb = state['can_succumb']
        return me

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
        self.can_skip = self._can_always_skip
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


    def player_won(self, i: int):
        self.remove_player(i)
        self.event(self._on_win, i)

    def remove_player(self, i: int):
        self.players.pop(i)
        old_phase = deepcopy(self.phase)

        def adjusted_phase(phase):
            return self.phase.match(
                do_queue = lambda p:
                    SjuanGameStatePhase.DO_QUEUE(adjusted_phase(p)),
                player_turn = lambda j:
                    SjuanGameStatePhase.PLAYER_TURN(j - 1 if j > i else j),
                give_cards = lambda j, n:
                    SjuanGameStatePhase.GIVE_CARDS(j - 1 if j > i else j, n)
            )
        self.phase = adjusted_phase(self.phase)

        self._turn_change(old_phase)


    def listen(
        self,
        on_turn_change: Optional[Callable[
            [SjuanGameStatePhase, SjuanGameStatePhase, bool],
            None
        ]] = None,
        on_win: Optional[Callable[
            [int], None
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
        if on_win:
            self._on_win.append(on_win)

    def event(self, evt, *args, **kwargs):
        for f in evt:
            f(*args, **kwargs)

from .rules import SjuanRules

class SjuanGame(Game[SjuanGameState, SjuanRules]):
    def __init__(self, num_players: int, cards = None, player_names = None):
        super().__init__()
        self._rules = SjuanRules
        self._num_players = num_players
        self._player_names = player_names
        self._cards = cards
        self._state = SjuanGameState(self._cards, self._num_players)

    @property
    def player_names(self):
        return self._player_names

    @property
    def rules(self):
        return self._rules

    @property
    def state(self):
        return self._state

    @property
    def cards(self):
        return self._cards

    @property
    def player_types(self):
        return self._player_types


    def reset(self):
        self._state.reset()
