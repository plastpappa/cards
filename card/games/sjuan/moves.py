from card import *
from .sjuan_card_stack import *


@adt
class SjuanAction:
    pass

@adt
class SjuanInsert:
    SJUAN_STACK: Case[SjuanCardStackInsert]
    PLAYER:      Case[int, CardHandInsert]

@adt
class SjuanTake:
    SRC_STACK: Case[CardStackTake]
    PLAYER:    Case[int, CardHandTake]
