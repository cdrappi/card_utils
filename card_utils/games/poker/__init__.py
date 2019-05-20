""" poker specific constants """

broadway_ranks = {'T', 'J', 'Q', 'K', 'A'}

STRAIGHT_FLUSH = 'straight flush'
QUADS = 'four of a kind'
FULL_HOUSE = 'full house'
FLUSH = 'flush'
STRAIGHT = 'straight'
THREE_OF_A_KIND = 'three of a kind'
TWO_PAIR = 'two pair'
ONE_PAIR = 'one pair'
HIGH_CARD = 'high card'

hand_order = {
    HIGH_CARD: 0,
    ONE_PAIR: 1,
    TWO_PAIR: 2,
    THREE_OF_A_KIND: 3,
    STRAIGHT: 4,
    FLUSH: 5,
    FULL_HOUSE: 6,
    QUADS: 7,
    STRAIGHT_FLUSH: 8
}

inverse_hand_order = {
    int_order: str_order
    for str_order, int_order in hand_order.items()
}
