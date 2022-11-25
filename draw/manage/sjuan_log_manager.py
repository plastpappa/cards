from collections import deque
from adt import adt, Case

from pyglet.graphics import Batch

from lib import *
from card import *
from card.games.sjuan import *
from draw.draw import *
from draw.vector import Vector


@adt
class PhaseLog:
    PLAY_CARDS: Case[int]
    GIVE_CARDS: Case[int, int]

@adt
class MoveLog:
    TO_STACK:      Case[int, Card]
    TO_PLAYER:     Case[int, int, Card]
    SKIP:          Case[int]
    ASK_FOR_CARDS: Case[int]


class LogManager:
    def __init__(
        self
    ):
        self._world = None
        self._log = []

    def init_world(self, world):
        self._world = world
        world.parent.game.listen(on_move = self._on_move)
        world.parent.game.state.listen(
            on_turn_change = self._on_turn_change
        )


    def player_name(self, p):
        return self._world._parent.player_name(p, False)

    def card_name(self, card):
        return f"{card.suit.icon()}{card.value.name_short()}"

    def phase_str(self, phase):
        game  = self._world._parent.game
        pname = self.player_name
        return phase.match(
            play_cards = lambda p:    f"{pname(p)}s tur | Lägg ett kort",
            give_cards = lambda p, n: f"{pname(p)}s tur | Ge {n} kort till "
                                       + pname(game.state.turn_incr(p, -1))
        )

    def move_str(self, move):
        game  = self._world._parent.game
        pname = self.player_name
        cname = self.card_name

        return move.match(
            to_stack = lambda p, card:
                f"{pname(p)} la in {cname(card)} i högen",
            to_player = lambda p1, p2, card:
                f"{pname(p1)} gav {cname(card)} till {pname(p2)}",
            skip = lambda p:
                f"{pname(p)} hoppade över sin tur",
            ask_for_cards = lambda p:
                f"{pname(p)} bad {pname(game.state.turn_incr(p, 1))} om kort"
        )

    def str_log(self):
        str = ''

        for phase, phase_events in self._log:
            str += '\n' + self.phase_str(phase)
            for move in phase_events:
                str += '\n      ' + self.move_str(move)

        return str[1:]


    def _on_turn_change(self, old_phase, new_phase, _):
        msg = new_phase.match(
            do_queue    = const(None),
            player_turn = lambda i: PhaseLog.PLAY_CARDS(i),
            give_cards  = lambda i, n: old_phase.match(
                do_queue    = const(PhaseLog.GIVE_CARDS(i, n)),
                give_cards  = const(None),
                player_turn = const(None) # will never happen
            )
        )

        if msg:
            print(self.phase_str(msg))
            self._log.append((msg, []))

    def _on_move(self, moves, state):
        # Ignore moves made during queue
        # (ie. handing out all the cards to people)
        if isinstance(moves, deque):
            return

        try:
            sub_log = self._log[-1][1]
        except IndexError as e:
            return

        sjuan         = self._world.parent.game
        curr_player_i = state.turn_index()
        curr_player   = state.players[curr_player_i]

        def sjuan_stack(take):
            ref_take, take_move = sjuan.rules.reference(take, state)
            cards = try_take(ref_take, take_move)
            if cards is not None:
                assert len(cards) == 1
                return MoveLog.TO_STACK(curr_player_i, cards[0])

        for move in moves:
            msg = move.match(
                from_to = lambda take, insert:
                    take.match(
                        src_stack = const(None),
                        myself    = lambda take_move:
                            insert.match(
                                sjuan_stack = lambda _: sjuan_stack(take),
                                player = lambda receiver_i, _:
                                    None if receiver_i == curr_player_i
                                    else take_move.match(
                                        hand_take = lambda card_i :
                                            MoveLog.TO_PLAYER(
                                                curr_player_i, receiver_i,
                                                curr_player.cards[card_i]
                                            )
                                    )
                            )
                    ),
                the_action = lambda action:
                    action.match(
                        skip          = const(MoveLog.SKIP(curr_player_i)),
                        ask_for_cards = const(MoveLog.ASK_FOR_CARDS(curr_player_i))
                    )
            )

            if msg is not None:
                print('    ' + self.move_str(msg))
                sub_log.append(msg)
