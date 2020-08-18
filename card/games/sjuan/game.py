import math
from collections import deque

from adt import adt, Case

from card import *
from card.game import Game
from .sjuan_card_stack import *
from .moves import *


@adt
class SjuanGameStatePhase:
    DO_QUEUE: Case[Optional[int]]
    PLAYER_TURN: Case[int]
    
    def next(self, num_players):
        # Queue None -> Turn  0
        # Turn  n    -> Queue n
        # Queue n    -> Turn  n+1
        return self.match(
            do_queue = lambda i:
                SjuanGameStatePhase.PLAYER_TURN(
                    (0 if i is None else i + 1) % num_players
                ),
            player_turn = lambda i:
                SjuanGameStatePhase.DO_QUEUE(i)
        )

class SjuanGameState:
    def __init__(self, num_players: int):
        self.queue = deque()
        self.phase = SjuanGameStatePhase.DO_QUEUE(None)
        
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
        
        for i in range(len(all_cards)):
            self.queue.append(SjuanRules.Move.FROM_TO(
                SjuanTake.SRC_STACK(CardStackTake.STACK_TAKE_TOP()),
                SjuanInsert.PLAYER(i % num_players, CardHandInsert.HAND_INSERT(0))
            ))
    
    def turn_incr(self, i: int, n: int):
        return (i + n) % len(self.players)
    
    def next_phase(self):
        self.phase = self.phase.next(len(self.players))
    
    def remove_player(self, i: int):
        self.players.pop(i)
        self.phase.match(
            do_queue = lambda j:
                SjuanGameStatePhase.DO_QUEUE(j - 1 if j > i else j),
            player_turn = lambda j:
                SjuanGameStatePhase.DO_QUEUE(j - 1 if j > i else j)
        )
    
    def turn_index(self):
        return self.phase.match(
            do_queue    = lambda i: i,
            player_turn = lambda i: i
        )


from .rules import SjuanRules

class SjuanGame(Game[SjuanGameState, SjuanRules]):
    def __init__(self, num_players: int):
        self.rules = SjuanRules
        self.state = SjuanGameState(num_players)
    
    def do(self, moves):
        return self.rules.do(moves, self.state)
        
    def moves_for_card(card):
        pass
        
    def suggested_moves():
        pass
