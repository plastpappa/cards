import os
import time
from datetime import datetime
import re
import copy as deepcopy
from pathlib import Path
import itertools
from functools import reduce

import pyglet
from card import *
from card.game import *
from card.games.sjuan import *
from train.playerbot import *
from train.io import *

from draw.draw import *
from draw.manage import *
from draw.games.sjuan import *
from lib import const, do_nothing


class Averager:
    def __init__(self):
        self.num      = 0
        self.sum      = 0
        self.last_100 = []

    def record(self, x):
        self.num += 1
        self.sum += x
        self.last_100.append(x)
        if len(self.last_100) > 100:
            self.last_100.pop(0)

    @property
    def avg(self):
        return self.sum / self.num

    def avg_n(self, n):
        if n > 100:
            raise ValueError(f"Must have n <= 100, got n = {n}")
        xs = self.last_100[-n:]
        return sum(xs) / len(xs)


def main(config, window, WINDOW_SIZE):
    cards_grouped = [ [
        Card(suit, value) for value in CardValue
        if ((value.adj_value(aces_lowest = True) - 7) * dir > 0
            or dir == 1 and value == CardValue.SEVEN)
    ] for suit in CardSuit for dir in (1, -1) ]
    cards_flat = [ x for group in cards_grouped for x in group ]

    N_players = 2

    names = [
        'Elioenai',
        'Gudrun',
        'Artemis',
        'Helah',
        'Drazen',
        'Lasse',
        'Ramiel',
        'Eyvindr',
        'Zhirayhr',
        'Brian',
        'Soma',
        'Gergely'
    ]
    bots = [ PlayerBot(None, cards_grouped, i, name = name) for i, name in enumerate(names) ]

    avg_badskips = [ Averager() for bot in bots ]
    def avgdata(avg):
        return f"{avg.avg} / {avg.avg_n(100)} / {avg.avg_n(40)} / {avg.avg_n(10)}"

    its = 0
    sessionsaver = SessionSaver(bots)

    chosen_bots = None
    while True:
        t0 = time.time()
        time_decisions = 0
        time_doing = 0

        # 60% chance to keep the match-up the same
        if chosen_bots is None or random.random() > 0.4:
            # Progressively add more and more bots
            num_available = 4 + its // 50
            available_bots = bots[:num_available]
            bot_tuples = list(itertools.combinations(enumerate(available_bots), N_players))
            # Sample in inverse proportion to how many games a bot has played
            tuple_weights = [
                reduce(lambda acc, bot: acc * 50 / (avg_badskips[bot[0]].num + 1), tuple, 1)
                for tuple in bot_tuples
            ]
            chosen_indices, chosen_bots = zip(*random.choices(list(bot_tuples), weights = tuple_weights)[0])

        player_config = [
            { 'type': 'human', 'name': bot.name } for bot in chosen_bots
        ]
        sjuan = Sjuan(player_config, RectangleShape(
            bottom_left = Vector(0, 0), size = Vector(900, 600)
        ), cards_grouped = cards_grouped, graphical = False)
        game = sjuan.game
        for i, bot in enumerate(chosen_bots):
            bot._sjuan = sjuan
            bot._index = i
        game.reset() # Seems to much improve speed - why? I'm not sure.

        trajectories = [ [] for bot in chosen_bots ]

        def update_last_turn_trajectories(fn):
            for i in range(N_players - 1):
                traj = trajectories[-(1 + i)]
                if len(traj) > 0:
                    last = traj[-1]
                    traj[-1] = (fn(i, last[0]), *last[1:])

        affect_gamma = 0.96
        def affect_last_turn_trajectories(x):
            update_last_turn_trajectories(lambda j, r:
               r + x * (affect_gamma ** j)
            )

        sessionsaver.new_iteration(game.state.players, chosen_indices)

        first = True
        who_started = None
        badskips = [ 0 for bot in chosen_bots ]

        time_init = time.time() - t0
        while not sjuan.done:
            t00 = time.time()
            game.state.phase.match(
                do_queue = lambda _: game.do(game.state.queue),
                player_turn = do_nothing, give_cards = do_nothing
            )

            curr_player_i = game.state.turn_index()
            curr_player   = game.state.players[curr_player_i]
            curr_bot      = chosen_bots[curr_player_i]
            curr_phase    = game.state.phase.match(
                do_queue = const(None), player_turn = const(0), give_cards = const(1)
            )

            if first:
                num_cards0 = [ len(player.cards) for player in game.state.players ]
                who_started = curr_player_i
                first = False

            num_cards_before = len(curr_player.cards)
            t01 = time.time()
            time_init_turn += t01 - t00
            move, log_prob, move_i, legal_moves = curr_bot.pick_move()
            t02 = time.time()
            time_decisions += t02 - t01
            game.do([ move ])
            sessionsaver.register_move(curr_phase, curr_player_i, move_i)
            num_cards_after = len(curr_player.cards)
            t03 = time.time()
            time_doing += t03 - t02

            my_reward = 0
            if sjuan.done: # (we won)    @TODO: make more general, ie make it work for >2 players
                my_reward += 2
                affect_last_turn_trajectories(-1.5)
            else:
                if move_i < curr_bot._num_groups:
                    my_reward += 0.1
                else:
                    move_i -= curr_bot._num_groups
                    if move_i == 0: # skip
                        my_reward -= 0.075
                        if len(legal_moves) > 1:
                            print("!!!! what????")
                        badskips[curr_player_i] += 1
                        affect_last_turn_trajectories(0.075)
                    elif move_i == 1: # ask for cards
                        if len(legal_moves) > 1:
                            badskips[curr_player_i] += 1
                        my_reward -= 0.5
                        affect_last_turn_trajectories(0.1)

            trajectories[curr_player_i].append(
                (my_reward, log_prob, curr_phase)
            )

            time_end += time.time() - t03

        t0_log = time.time()
        winner_i = curr_player_i
        num_cards = [ len(player.cards) for player in game.state.players ]
        num_cards.insert(winner_i, 0)

        its += 1
        print('')
        print(f'[><] FINISHED EPISODE {its}')
        for i, bot in enumerate(chosen_bots):
            real_i = chosen_indices[i]
            avg_badskips[real_i].record(badskips[i])
            loss_play, loss_give = bot.do_training(trajectories[i])

            s = f'        {bot.name} | '
            p = ' ' * len(s)
            print(s + f'Loss:           turns {loss_play}, giving cards {loss_give}')
            print(p + f'Went first?:    {who_started == i}')
            print(p + f'Cards to start: {num_cards0[i]}')
            print(p + f'Cards left:     {num_cards[i]}')
            print(p + f'Skips:          {badskips[i]}')
            print(p + f'Average skips:  {avgdata(avg_badskips[real_i])}')
            print(p + f'Num matches:    {avg_badskips[real_i].num}')
        print('')
        t_final = time.time()
        print(f'Elapsed time: {t_final - t0}s ({time_init} / {time_decisions} / {} / {time_doing}')
        print('\n')

        if its % 300 == 0:
            print('[[SAVING]] [[SAVING]] [[SAVING]] [[SAVING]]')
            sessionsaver.save()
            print('\n')
