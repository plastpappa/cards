from card import *
from .sjuan_card_stack import *


@adt
class SjuanAction:
    SKIP:          Case
    ASK_FOR_CARDS: Case
    
    def __str__(self):
        return self.match(
            skip          = lambda: "skip",
            ask_for_cards = lambda: "ask for cards"
        )

@adt
class SjuanInsert:
    SJUAN_STACK: Case[SjuanCardStackInsert]
    PLAYER:      Case[int, CardHandInsert]
    
    def __str__(self):
        return self.match(
            sjuan_stack = lambda    i: f"sjuan stack [{i}]",
            player      = lambda n, i: f"player #{n} [{i}]"
        )

@adt
class SjuanTake:
    SRC_STACK: Case[CardStackTake]
    MYSELF:    Case[CardHandTake]
    
    def __str__(self):
        return self.match(
            src_stack = lambda i: f"source stack [{i}]",
            myself    = lambda i: f"themselves [{i}]"
        )
