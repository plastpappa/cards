import copy as deepcopy
import random
import math
import time
from yaml import load, Loader

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical

from card import *
from card.game import *
from card.games.sjuan import *

from draw.draw import *
from draw.manage import *
from draw.games.sjuan import *
from lib import const, do_nothing


gamma = 0.9948

class PlayerTurnModel(nn.Module):
    def __init__(self, input_shape, num_groups, name):
        super().__init__()

        self.input_shape = input_shape
        self.num_groups = num_groups
        self.name = name

        self.output_shape = self.num_groups + 1   # + 2
        self.model = nn.Sequential(
            nn.Linear(self.input_shape, 128),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, self.output_shape)
        )
        self.optimiser = optim.Adam(self.parameters(), lr = 0.015)

        self.train() # Set training mode


    def choice_to_move(self, real_item_i, my_cards, stack_cards):
        if real_item_i < self.num_groups:
            suit = CardSuit(1 + real_item_i // 2)
            try:
                cards = stack_cards[suit]
                if real_item_i % 2 == 0:
                    card = deepcopy(cards[0])
                    card.value -= 1
                else:
                    card = deepcopy(cards[len(cards) - 1])
                    card.value += 1
            except (IndexError, KeyError):
                card = None

            if card:
                try:
                    take = SjuanTake.MYSELF(CardHandTake.HAND_TAKE(
                        my_cards.index(card)
                    ))
                except ValueError:
                    take = None
            else:
                try:
                    matches = [
                        (i, card) for i, card in enumerate(my_cards)
                        if card.suit == suit and card.value == CardValue.SEVEN
                    ]
                    index = matches[0][0]
                    take = SjuanTake.MYSELF(CardHandTake.HAND_TAKE(index))
                except IndexError:
                    take = None

            if take:
                move = SjuanRules.Move.FROM_TO(
                    take,
                    SjuanInsert.SJUAN_STACK(SjuanCardStackInsert.SJUAN_INSERT())
                )
            else:
                move = None
        elif real_item_i == self.num_groups:
            move = SjuanRules.Move.THE_ACTION(SjuanAction.SKIP())
        #elif real_item_i == self.num_groups + 1:
        #    move = SjuanRules.Move.THE_ACTION(SjuanAction.ASK_FOR_CARDS())
        else:
            raise f"Oopsie! {real_item_i}"

        return move

    def do_training(self, loss):
        self.optimiser.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 0.8)
        self.optimiser.step()

class GiveCardsModel(nn.Module):
    def __init__(self, input_shape, num_groups, name):
        super().__init__()

        self.input_shape = input_shape
        self.num_groups = num_groups
        self.name = name

        self.output_shape = self.num_groups
        self.model = nn.Sequential(
            nn.Linear(self.input_shape, 128),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, self.output_shape)
        )
        self.optimiser = optim.Adam(self.parameters(), lr = 0.01)

        self.train() # Set training mode


    def choice_to_move(self, real_item_i, my_cards, next_player_i):
        suit = CardSuit(1 + real_item_i // 2)
        try:
            cards = [ (i, card) for i, card in enumerate(my_cards) if card.suit == suit ]
            cards.sort(key = lambda card: card[1].value.adj_value(aces_lowest = True))

            if real_item_i % 2 == 0:
                card_i = cards[0][0]
            else:
                card_i = cards[len(cards) - 1][0]

            return SjuanRules.Move.FROM_TO(
                SjuanTake.MYSELF(CardHandTake.HAND_TAKE(card_i)),
                SjuanInsert.PLAYER(next_player_i, CardHandInsert.HAND_INSERT(0))
            )
        except IndexError:
            return None

    def do_training(self, loss):
        self.optimiser.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 0.8)
        self.optimiser.step()


class PlayerBot():
    def __init__(self, sjuan, all_cards, i: int, name: str = "unnamed"):
        self._sjuan = sjuan
        self._all_cards = all_cards
        self._index = i
        self._name = name

        self._num_cards   = sum(len(group) for group in all_cards)
        self._num_groups  = len(all_cards)
        self._input_shape = 3 * self._num_cards
        self._player_turn_model = PlayerTurnModel(self._input_shape, self._num_groups, name)
        self._give_cards_model  = GiveCardsModel(self._input_shape, self._num_groups, name)


    @property
    def sjuan(self):
        return self._sjuan

    @sjuan.setter
    def sjuan(self, sjuan):
        self._sjuan = sjuan

    @property
    def all_cards(self):
        return self._all_cards

    @property
    def index(self):
        return self._index

    @property
    def name(self):
        return self._name


    def get_state_representation(self):
        state = self._sjuan.game.state
        me    = state.players[self._index]

        # Canonical sorting so that symmetries are preserved
        # (groups where we own the last card are first, then those where we own the second, etc.)
        def key(x):
            j, group = x
            return sum(c << i for i, c in enumerate((card in me.cards) for card in group))
        indices, groups = zip(*sorted(enumerate(self.all_cards), key = key))
        cards_flat = [ c for group in groups for c in group ]

        fmine = torch.tensor([
            (card in me.cards) for card in cards_flat
        ], dtype = torch.float)
        fstack = torch.tensor([
            (card in [card for cards in state.sjuan_stack.cards.values() for card in cards]) for card in cards_flat
        ], dtype = torch.float)
        ftheirs = torch.tensor([
            not (fmine[i] or fstack[i]) for i in range(len(cards_flat))
        ], dtype = torch.float)

        return torch.cat((fmine, fstack, ftheirs)), indices


    def real_move_i(self, action_item, indices):
        if action_item < self._num_groups:
            return indices[action_item]
        else:
            return action_item

    def get_probability_distribution(self):
        state = self._sjuan.game.state
        me    = state.players[self._index]
        state_repr, indices = self.get_state_representation()

        def player_turn(item_i):
            return self._player_turn_model.choice_to_move(item_i, me.cards, state.sjuan_stack.cards)
        def give_cards(item_i):
            return self._give_cards_model.choice_to_move(item_i, me.cards, state.turn_incr(self._index, 1))
        f, model = state.phase.match(
            player_turn = const((player_turn, self._player_turn_model)),
            give_cards  = const((give_cards, self._give_cards_model)),
            do_queue    = const(None)
        )

        logits = model.model(state_repr)
        legal_logits = torch.empty(len(logits))
        moves        = []
        legal_moves  = []
        for i, logit in enumerate(logits):
            real_i = self.real_move_i(i, indices)
            move = f(real_i)
            legal = move is not None and self._sjuan.game.is_valid([ move ])
            # Only allow skips/card takes when no moves are legal
            legal = legal and move.match(the_action = const(len(legal_moves) == 0), from_to = const(True))
            legal_logits[i] = logit if legal else -math.inf
            moves.append((move, real_i))
            if legal:
                legal_moves.append((move, real_i))

        cat_legal = Categorical(logits = legal_logits)
        cat0 = Categorical(logits = logits)

        """if random.random() <= 0.02:
            state = self._sjuan.game.state
            print(f"({self.name}) Cards:", [ str(card) for card in state.players[self._index].cards ])
            print(f"({self.name}) Stack:", [ str(card) for card in
                [ card for cards in state.sjuan_stack.cards.values() for card in cards ]
            ])
            print(f"({self.name}) Probability distribution:",
                [ f"Move[{moves[i]}]: {prob * 100}%" for i, prob in enumerate(cat0.probs) ]
            )"""

        return cat_legal, cat0, moves, legal_moves


    def pick_move(self):
        pd, pd0, moves, legal_moves = self.get_probability_distribution()
        action = pd.sample()
        move, item_i = moves[action.item()]
        return move, pd0.log_prob(action), item_i, legal_moves

    def pick_most_likely_move(self):
        pd, pd0, moves, legal_moves = self.get_probability_distribution()
        action_item, prob = max(enumerate(pd.probs), key = lambda x: x[1])
        move, item_i = moves[action_item]
        return move, prob, item_i, legal_moves


    def do_training(self, trajectory):
        T = len(trajectory)
        rewards   = [ t[0] for t in trajectory ]
        log_probs = [ t[1] for t in trajectory ]
        type      = [ t[2] for t in trajectory ]

        log_probs_turn = []
        rets_turn      = []
        log_probs_give = []
        rets_give      = []
        ret = 0.0
        for t in reversed(range(T)):
            ret = rewards[t] + gamma * ret
            if type[t] == 0:
                rets_turn.append(ret)
                log_probs_turn.append(log_probs[t])
            else:
                rets_give.append(ret)
                log_probs_give.append(log_probs[t])

        avg_ret = ret / T
        if len(log_probs_turn) > 0:
            loss_turn = torch.sum(-torch.stack(log_probs_turn) * (torch.tensor(rets_turn) - avg_ret))
            self._player_turn_model.do_training(loss_turn)
        else:
            loss_turn = 0
        if len(log_probs_give) > 0:
            loss_give = torch.sum(-torch.stack(log_probs_give) * (torch.tensor(rets_give) - avg_ret))
            self._player_turn_model.do_training(loss_give)
        else:
            loss_give = 0

        return loss_turn, loss_give
