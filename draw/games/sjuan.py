from pathlib import Path

from card import *
from card.game import *
from card.games.sjuan import *

from draw.draw import *
from draw.shape import RectangleShape
from draw.vector import Vector
from draw.manage import *
from lib import const, do_nothing

import torch
from train.playerbot import PlayerBot


class Sjuan:
    def __init__(self, players, bounds: RectangleShape, cards_grouped = None, graphical: bool = True):
        if cards_grouped is None:
            cards_grouped = [ [
                Card(suit, value) for value in CardValue
                if ((value.adj_value(aces_lowest = True) - 7) * dir > 0
                    or dir == 1 and value == CardValue.SEVEN)
            ] for suit in CardSuit for dir in (1, -1) ]
        cards_flat = [ x for group in cards_grouped for x in group ]

        game = SjuanGame(
            len(players), cards_flat, [ player['name'] for player in players ]
        )
        self._game = game
        self._players = players

        self._bounds = bounds
        self._done   = False
        self.graphical = graphical

        self._world = World(self)

        if graphical:
            self._source_stack_manager = CardStackManager(
                game.state.source_stack, bounds.centre,
                label = None, interactable = False
            )
            self._world.add_object(self._source_stack_manager)

            self._sjuan_stack_manager = SjuanStackManager(
                game.state.sjuan_stack, bounds.centre
            )
            self._sjuan_stack_manager._drawer.visible = False
            self._world.add_object(self._sjuan_stack_manager)

            self._player_managers = []
            self._bots = []
            for i, player in enumerate(game.state.players):
                player_config = players[i]
                manager = CardHandManager(
                    player, Vector(0, 0), label = "Player"
                )
                self._player_managers.append(manager)
                self._world.add_object(manager)
                if player_config['type'] == 'robot':
                    bot = PlayerBot(self, cards_grouped, i, name = game.player_names[i])
                    checkpoint = torch.load(Path.cwd() / player_config['file'])
                    bot._player_turn_model.model.load_state_dict(checkpoint['player_turn_model'])
                    bot._give_cards_model.model.load_state_dict(checkpoint['give_cards_model'])
                    bot._player_turn_model.model.eval()
                    bot._give_cards_model.model.eval()
                    self._bots.append(bot)
                else:
                    self._bots.append(None)

            self._advance_turn_button = ButtonManager(
                "Next turn", font_size = 11,
                bounds = RectangleShape(
                    centre = self._bounds.centre - Vector(0, 80),
                    size   = Vector(160, 34)
                ),
                on_click = lambda: self._game.do(self._game.state.queue),
                background_colour   = (126, 224, 239, 190),
                background_colour_2 = (96,  205, 222, 175),
                outline_colour      = (130, 216, 248, 230)
            )
            # self._world.add_object(self._advance_turn_button)

        # self._world.add_object(LogManager())

        self._player_amount_changed()
        self._adjust_player_managers()
        game.state.phase.match(
            do_queue = self._queue_time,
            player_turn = do_nothing, give_cards = do_nothing
        )

        # Events

        def player_won(i):
            if self.graphical:
                self._world.remove_object(self._player_managers[i])
                self._player_managers.pop(i)
            self._player_amount_changed()
            if len(self.game.state.players) <= 1:
                self._done = True
                self._world.game_over()

        game.state.listen(on_win = player_won)

        if graphical:
            self._botting = False
            def do_bot_stuff(i):
                def queue():
                    self._botting = False
                    self._game.do(self._game.state.queue)

                bot = self._bots[i]
                if bot:
                    self._botting = True

                    move, prob, item_i, legal_moves = bot.pick_most_likely_move()
                    self._game.do([ move ])
                    self._game.state.phase.match(
                        do_queue    = lambda _: queue(),
                        player_turn = lambda j: do_bot_stuff(j),
                        give_cards  = lambda j, _: do_bot_stuff(j)
                    )

                    return True
                else:
                    return False

            def turn_change(old_phase, new_phase, players_changed):
                if not self._botting:
                    def new_player_turn(i, giving_cards):
                        try:
                            self._world.remove_object(self._advance_turn_button)
                        except ValueError:
                            pass

                        if not do_bot_stuff(i):
                            self._adjust_player_managers(curr_turn = i)
                            if not self._skip_turn_button:
                                update_skip_button(self._game.state.can_skip, can_create = True)

                    new_phase.match(
                        do_queue = lambda next_phase:
                            self._queue_time(next_phase),
                        player_turn = lambda i: new_player_turn(i, False),
                        give_cards  = lambda i, _: new_player_turn(i, True)
                    )

                    if not self._ask_cards_button:
                        update_ask_cards_button(self._game.state.can_succumb)

            self._skip_turn_button = None
            def update_skip_button(skippable, can_create = False):
                if not self._skip_turn_button:
                    if can_create:
                        curr_player  = self._player_managers[self._game.state.turn_index()]
                        cards_bounds = curr_player._drawer._bounds_inner
                        size         = Vector(130, 18)
                        self._skip_turn_button = ButtonManager(
                            "Skip turn", font_size = 10,
                            bounds = RectangleShape(
                                bottom_left = (
                                    cards_bounds.bottom_right
                                    + Vector(0, cards_bounds.size.y / 2)
                                    - Vector(size.x / 2, size.y / 2)
                                    + Vector(0, 50)
                                ), size = size
                             ),
                            on_click = lambda: self._game.do([
                                SjuanRules.Move.THE_ACTION(SjuanAction.SKIP())
                            ]),
                            background_colour   = (126, 224, 239, 220),
                            background_colour_2 = (96,  205, 222, 200),
                            outline_colour      = (130, 216, 248, 255)
                        )
                    else:
                        return

                if skippable:
                    self._world.add_object(self._skip_turn_button)
                else:
                    try:
                        self._world.remove_object(self._skip_turn_button)
                    except ValueError:
                        pass

            self._ask_cards_button = None
            def update_ask_cards_button(can_ask):
                if not self._ask_cards_button:
                    curr_i       = self._game.state.turn_index()
                    prev_i       = self._game.state.turn_incr(curr_i, -1)
                    prev_player  = self._player_managers[prev_i]
                    cards_bounds = prev_player._drawer._bounds_inner
                    size         = Vector(130, 18)
                    self._ask_cards_button = ButtonManager(
                        "Ask for cards", font_size = 10,
                        bounds = RectangleShape(
                            bottom_left = (
                                cards_bounds.bottom_right
                                + Vector(0, -cards_bounds.size.y / 2)
                                - Vector(size.x / 2, -size.y / 2)
                                - Vector(15, 10)
                            ), size = size
                         ),
                        on_click = lambda: self._game.do([
                            SjuanRules.Move.THE_ACTION(SjuanAction.ASK_FOR_CARDS())
                        ]),
                        background_colour   = (244, 174, 169, 220),
                        background_colour_2 = (230,  169, 160, 200),
                        outline_colour      = (255, 146, 158, 255)
                    )

                if can_ask:
                    self._world.add_object(self._ask_cards_button)
                else:
                    try:
                        self._world.remove_object(self._ask_cards_button)
                    except ValueError:
                        pass

            game.state.listen(
                on_turn_change        = turn_change,
                on_skippable_change   = update_skip_button,
                on_succumbable_change = update_ask_cards_button
            )

    def reset(self):
        self._game.reset()
        self._done = False

    @property
    def game(self):
        return self._game

    @property
    def done(self):
        return self._done

    def player_name(self, index, is_active):
        try:
            name = self.game.player_names[index]
        except (TypeError, IndexError):
            name = f"Player {index + 1}"
        return name + (" (your turn)" if is_active else "")

    def _player_amount_changed(self):
        if self.graphical:
            PAD = 44

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
                raise "Too many players"

    def _adjust_player_managers(self, curr_turn: Optional[int] = None):
        if self.graphical:
            N = len(self._player_managers)
            if curr_turn is None:
                curr_turn_ = 0
            else:
                curr_turn_ = curr_turn
                self._sjuan_stack_manager._drawer.visible = True

            for j, player_manager in enumerate(self._player_managers):
                player_manager.set_target(None)
                player_manager.pause = False

                data = self._player_ps[(curr_turn_ + j) % N]
                player_manager.rotation = data[0]
                player_manager.pos      = data[1]

                is_curr_active = (curr_turn == j)
                player_manager._drawer.hidden = not is_curr_active
                player_manager.controllable   = is_curr_active
                player_manager.label = self.player_name(j, is_curr_active)

    def _queue_time(self, next_phase):
        if self.graphical:
            for j, player_manager in enumerate(self._player_managers):
                player_manager.pause          = True
                player_manager._drawer.hidden = True
                player_manager.controllable   = False

            self._advance_turn_button.label = next_phase.match(
                do_queue    = const(""),  # Never two queues in a row, so..
                player_turn = const("Next turn"),
                give_cards  = const("Give cards")
            )

            self._world.add_object(self._advance_turn_button)

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
                return self._sjuan_stack_manager._drawer.position_for(card)

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
