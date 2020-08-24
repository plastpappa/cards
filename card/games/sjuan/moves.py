from card import *
from .sjuan_card_stack import *


@adt
class SjuanAction:
    pass

@adt
class SjuanInsert:
    SJUAN_STACK: Case[SjuanCardStackInsert]
    PLAYER:      Case[int, CardHandInsert]
    
    def __str__(self):
        return self.match(
            sjuan_stack = lambda i:    f"sjuan stack [{i}]",
            player      = lambda n, i: f"player #{n+1} [{i}]"
        )

@adt
class SjuanTake:
    SRC_STACK: Case[CardStackTake]
    PLAYER:    Case[int, CardHandTake]
    
    def __str__(self):
        return self.match(
            src_stack = lambda i:    f"source stack [{i}]",
            player    = lambda n, i: f"player #{n+1} [{i}]"
        )
