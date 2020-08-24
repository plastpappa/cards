from card import *
from card.game import *
from card.games.sjuan import *

from draw.draw import *
from draw.shape import RectangleShape
from draw.vector import Vector
from draw.manage import *


class Sjuan:
    def __init__(self, game: SjuanGame, bounds: RectangleShape):
        self._game   = game
        self._bounds = bounds
        
        self._world = World(self)
        
        self._source_stack_manager = CardStackManager(
            game.state.source_stack, bounds.centre,
            label = None, interactable = False
        )
        self._world.add_object(self._source_stack_manager)
        
        self._sjuan_stack_manager = SjuanStackManager(
            game.state.sjuan_stack, bounds.centre
        )
        
        self._player_managers = []
        for player in game.state.players:
            manager = CardHandManager(
                player, Vector(0, 0), label = "Spelare"
            )
            self._player_managers.append(manager)
            self._world.add_object(manager)
        
        self._player_amount_changed()
        self._adjust_player_managers()
    
    def _player_amount_changed(self):
        PAD = 44
        pi = math.pi
        
        num_ps = len(self._game.state.players)
        if num_ps == 1:
            self._player_ps = [
                (0, self._bounds.bottom_centre + Vector(0, PAD))
            ]
        elif num_ps == 2:
            self._player_ps = [
                (0,   self._bounds.bottom_centre + Vector(0, PAD)),
                (180, self._bounds.top_centre    - Vector(0, PAD))
            ]
        elif num_ps == 3:
            self._player_ps = [
                (0,   self._bounds.bottom_centre + Vector(0, PAD)),
                (270, self._bounds.centre_left   + Vector(PAD, 0)),
                (90,  self._bounds.centre_right  - Vector(PAD, 0))
            ]
        elif num_ps == 4:
            self._player_ps = [
                (0,   self._bounds.bottom_centre + Vector(0, PAD)),
                (270, self._bounds.centre_left   + Vector(PAD, 0)),
                (180, self._bounds.top_centre    - Vector(0, PAD)),
                (90,  self._bounds.centre_right  - Vector(PAD, 0))
            ]
        else:
            raise "Oops"
    
    def _adjust_player_managers(self):
        curr_turn_ = self._game.state.turn_index()
        curr_turn = 0 if curr_turn_ is None else curr_turn_
        N = len(self._player_managers)
        
        for j, player_manager in enumerate(self._player_managers):
            data = self._player_ps[(curr_turn + j) % N]
            player_manager.set_target(None)
            player_manager._drawer.hidden = (curr_turn_ != j)
            player_manager.controllable   = (curr_turn_ == j)
            player_manager.label    = (f"Spelare {j+1}"
                                      + (" (du)" if curr_turn_ == j else ""))
            player_manager.rotation = data[0]
            player_manager.pos      = data[1]
            
            
    def target_position(self, take: SjuanTake, insert: SjuanInsert):
        def hand_insert(player_i, card_i):
            drawer = self._player_managers[player_i]._drawer
            card = drawer.nth_card(card_i)
            if card is not None and card.batch is not None:
                return card.centre
        
        def sjuan_stack():
            ref_take, take_move = self._game.rules.reference(take, self._game.state)
            cards = try_take(ref_take, take_move)
            if cards is not None:
                assert len(cards) == 1
                card = cards[0]
                return self._sjuan_stack_manager.pos
        
        return insert.match(
            sjuan_stack = lambda _: sjuan_stack(),
            player = lambda player_i, insert2: insert2.match(
                hand_insert = lambda card_i: hand_insert(player_i, card_i)
            )
        )
    
    def moves_for_card(self, card_i: int):
        moves = self._game.moves_for_card(card_i)
        return [ x for x in [
            (move, self.target_position(take, insert))
            for move, take, insert in moves
        ] if x[1] is not None ]  # Silly Python.
