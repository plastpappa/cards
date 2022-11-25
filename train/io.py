import os
import math
import re
from datetime import datetime
from pathlib import Path

import torch
from bitarray import bitarray

from card import *


def get_date():
    return re.sub(r'\.\d+', '', str(datetime.now()).replace(':', ''))


def bits(n, numbits = None):
    bits = bin(n)[2:]
    if numbits is not None and len(bits) > numbits:
        raise OverflowError(f'Value {n} does not fit in {numbits} bits')
    return bitarray(bits.zfill(numbits))

def num(bits):
    return sum(c << i for i, c in enumerate(reversed(bits)))


bits_per_card = math.ceil(math.log2(52))

def card_to_bits(card):
    return bits(1 + (card.suit.value - 1) * 13 + (card.value.value - 2), bits_per_card)

def num_to_card(n):
    n -= 1
    return Card(CardSuit(1 + n // 13), CardValue(2 + n % 13))


class SessionSaver:
    def __init__(self, bots, extraname = None):
        self._bots = bots

        self._bits_per_phase  = 1
        self._bits_per_player = math.ceil(math.log2(1 + len(bots)))
        self._bits_per_move   = math.ceil(math.log2(10))

        self._foldername = f'Session{(" " + extraname if extraname else "")} {get_date()}'
        self._root = Path.cwd() / 'saved_models'
        self._dir  = (self._root / self._foldername).resolve()
        os.makedirs(self._dir)

        self._its = 0
        self.reset_bits()


    def write_bits(self, x):
        self._bits.extend(x)

    def reset_bits(self):
        self._bits = bitarray([])
        self.write_bits(bits(self._bits_per_player, 8))
        self.write_bits(bits(self._bits_per_move,   8))


    def new_iteration(self, players, indices):
        self._its += 1
        if self._its > 1:
            self.write_bits(bits(0, self._bits_per_phase + self._bits_per_player + self._bits_per_move))
        for i, player in enumerate(players):
            self.write_bits(bits(1 + indices[i], self._bits_per_player))
            for card in player.cards:
                self.write_bits(card_to_bits(card))
            self.write_bits(bits(0, bits_per_card))
        self.write_bits(bits(0, self._bits_per_player))

    def register_move(self, phase_i, player_i, move_i):
        self.write_bits(bits(phase_i,  self._bits_per_phase))
        self.write_bits(bits(player_i, self._bits_per_player))
        self.write_bits(bits(move_i,   self._bits_per_move))


    def save(self):
        localname = f'{self._its} iterations ({get_date()})'
        localpath = self._dir / localname
        os.makedirs(localpath)

        models_path = (localpath / 'models').resolve()
        os.makedirs(models_path)
        for i, bot in enumerate(self._bots):
            torch.save({
                'player_turn_model': bot._player_turn_model.model.state_dict(),
                'give_cards_model':  bot._give_cards_model.model.state_dict()
            }, models_path / f'{bot.name}.bot')

        file_path = (localpath / 'games.data').resolve()
        with open(file_path, 'wb') as file:
            self._bits.tofile(file)
        self.reset_bits()


class SessionReader:
    def __init__(self, dirpath, names):
        self._dirpath = dirpath
        self._bits    = bitarray([])
        self._names   = names

        file_path = (dirpath / 'games.data').resolve()
        with open(file_path, 'rb') as file:
            self._bits.fromfile(file)

        self._bits_per_phase  = 1
        self._bits_per_player = num(self.read_bits(8))
        self._bits_per_move   = num(self.read_bits(8))

    def read_bits(self, n):
        bits = []
        i = n
        while i > 0:
            bits.append(self._bits.pop(0))
            i -= 1
        return bits


    def read_iteration(self):
        # Read player hands
        player_names = []
        player_hands = []
        all_cards    = []
        new = True
        while True:
            if new:
                player_i = num(self.read_bits(self._bits_per_player))
                if player_i == 0:
                    break
                else:
                    player_hands.append([])
                    player_names.append(self._names[player_i - 1])
                new = False
            else:
                card_num = num(self.read_bits(bits_per_card))
                if card_num == 0:
                    new = True
                else:
                    card = num_to_card(card_num)
                    player_hands[-1].append(card)
                    all_cards.append(card)
        player_hands_original = deepcopy(player_hands)

        # Initialise game
        game = SjuanGame(num_players = len(player_hands),
                         cards       = all_cards,
                         hands       = player_hands
                         )

        # Read player hands
        stack = {}

        return player_hands
