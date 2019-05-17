""" util functions for omaha games """
from card_utils.deck import value_to_rank
from card_utils.deck.utils import (
    rank_partition,
    suit_partition,
    ranks_to_sorted_values,
)


def _validate_board(board):
    """ raise exception if board doesn't have exactly 5 cards
    :param board: ([str]) list of 5 cards
    :return:
    """
    if len(board) != 5:
        raise ValueError(
            f'omaha.utils.get_best_hand: '
            f'board must have 5 cards\n'
            f'input: {board}'
        )


def _validate_hands(hands):
    """ raise exception if all hands don't have exactly 4 cards

    :param hands: ([[str]]) list of list of 4 cards
    :return: None
    """
    for hand in hands:
        if len(hand) != 4:
            raise ValueError(
                f'omaha.utils._validate_hands: '
                f'all hands must have 4 cards\n'
                f'invalid hand: {hand}'
            )


def get_suit_with_gte_3_cards(board_by_suits):
    for suit, ranks in board_by_suits.items():
        if len(ranks) >= 3:
            return suit

    return None


def _get_straight_values(v1, v2, v3):
    """
    :param v1: (int)
    :param v2: (int)
    :param v3: (int)
    :return: (set(tuple(int))) set of tuples of ints
    """
    straight_range = 3 + v1 - v3
    if straight_range <= 0:
        return set()

    cards_on_board = {v1, v2, v3}
    start_value = max(1, v1 - straight_range)
    end_value = min(14, v3 + straight_range)

    straight_values = set()
    for lowest_value in range(start_value, end_value):
        straight_values = set(range(lowest_value, lowest_value + 5))
        in_hand_values = straight_values.difference(cards_on_board)
        straight_values.add(tuple(in_hand_values))

    return straight_values


def get_possible_straights(ranks):
    """ get a list of hole card combinations
        that could make a straight
        on a board with these ranks

    :param ranks: ([str])
    :return: ([[str]]) list of list of ranks
    """
    if len(ranks) < 3:
        # need 3 cards to make a straight
        return []

    values = ranks_to_sorted_values(
        ranks=ranks,
        aces_high=True,
        aces_low=True
    )

    possible_straight_values = set()
    for v1, v2, v3 in zip(values[0:-2], values[1:-1], values[2:]):
        possible_straight_values.add(_get_straight_values(v1, v2, v3))

    return [
        [value_to_rank[v] for v in straight_value_set]
        for straight_value_set in possible_straight_values
    ]


def get_possible_straight_flushes(ranks, suit):
    """ get a list of possible hole cards that could make straight flushes
        if we have these ranks on the board in this suit

    :param ranks: ([str]) e.g. ['J', 'Q', 'K']
    :param suit: (str) e.g. 'c'
    :return: ([[str]]) e.g. [['9c', 'Tc'], ['Tc', 'Ac']]
    """
    return [
        [f'{r}{suit}' for r in possible_straight_ranks]
        for possible_straight_ranks in get_possible_straights(ranks)
    ]


def get_best_hand(board, hands):
    """
    hand ranks go:

    STRAIGHT FLUSH:  starting with A-high (T-J-Q-K-A)
                     down to       A-low  (A-2-3-4-5)

    FOUR OF A KIND:  starting with quad A (A-A-A-A-x)
                     down to       quad 2 (2-2-2-2-x)
        --> though this is irrelevant in omaha,
            tiebreaker goes to best kicker.
            (this applies to all non-straight/flush hands)

    FULL HOUSE:      starting with A full of K (A-A-A-K-K)
                     down to       2 full of 3 (2-2-2-3-3)

    FLUSH:           starting with A-high (A-K-Q-J-9)
                     down to       7-high (7-5-4-3-2)

    STRAIGHT:        starting with "broadway" (T-J-Q-K-A)
                     down to      "the wheel" (A-2-3-4-5)

    THREE OF A KIND: starting with three aces (A-A-A-K-Q)
                     down to     three deuces  (2-2-2-3-4)

    TWO-PAIR:        starting with aces up (A-A-K-K-Q)
                     down to    3s over 2s (3-3-2-2-4)

    ONE-PAIR:        starting with aces (A-A-K-Q-J)
                     down to deuces     (2-2-5-4-3)

    HIGH CARD:       starting with ace high (A-K-Q-J-9)
                     down to         7 high (7-5-4-3-2)

    :param board: ([str]) list of 5 cards
    :param hands: ([[str]]) list of list of 4 cards
    :return: (int) index of `hands` that makes the strongest omaha hand
    """
    _validate_board(board)
    _validate_hands(hands)

    board_by_suits = suit_partition(board)
    flush_suit = get_suit_with_gte_3_cards(board_by_suits)

    if flush_suit is not None:
        possible_straight_flushes = get_possible_straight_flushes(
            ranks=board_by_suits[flush_suit],
            suit=flush_suit
        )
        if possible_straight_flushes:
            pass

    board_by_ranks = rank_partition(board)
