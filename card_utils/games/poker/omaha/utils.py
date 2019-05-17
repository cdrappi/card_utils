""" util functions for omaha games """
from card_utils.deck import value_to_rank, rank_to_value
from card_utils.deck.utils import (
    rank_partition,
    suit_partition,
    ranks_to_sorted_values,
)
from card_utils.games.poker import broadway_ranks


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
    straight_range = 3 + v1 - v3  # TODO: better variable name... gaps?
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


def get_best_straight_flush_if_any(possible_straight_flushes, hands, suit):
    """

    :param possible_straight_flushes: (
    :param hands: ([[str]])
    :param suit: (str)
    :return: (int) index of `hands` holding best straight flush
    """
    # TODO: shorter + clearer variable names
    highest_straight_flush_hand_index = None
    overall_max_connecting_card_value = 0
    for ii, hand in enumerate(hands):
        # TODO: this is terrible, clean up
        hand_set = set(hand)
        for sf in possible_straight_flushes:
            connecting_cards = set(sf).union(hand_set)
            if len(connecting_cards) == 2:
                if connecting_cards < {f'{r}{suit}' for r in broadway_ranks}:
                    # royal flush! can return here, since it is unique in omaha
                    return ii
                max_connecting_value = max(rank_to_value[r] for r, _ in connecting_cards)
                if max_connecting_value > overall_max_connecting_card_value:
                    highest_straight_flush_hand_index = ii
                    overall_max_connecting_card_value = max_connecting_value

    return highest_straight_flush_hand_index


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
    :return: ([int]) indices of `hands` that makes the strongest omaha hand,
        --> this is a list because it is possible to "chop" with
            every hand rank except straight flushes, quads and flushes
    """
    _validate_board(board)
    _validate_hands(hands)

    board_by_suits = suit_partition(board)
    flush_suit = get_suit_with_gte_3_cards(board_by_suits)

    # Check to see if anyone has a straight flush
    if flush_suit is not None:
        possible_straight_flushes = get_possible_straight_flushes(
            ranks=board_by_suits[flush_suit],
            suit=flush_suit
        )
        if possible_straight_flushes:
            best_straight_flush_index = get_best_straight_flush_if_any(
                possible_straight_flushes=possible_straight_flushes,
                hands=hands,
                suit=flush_suit
            )
            if best_straight_flush_index is not None:
                return [best_straight_flush_index]

    # If the board is paired, we could have quads or a full house
    board_by_ranks = rank_partition(board)
    is_paired_board = any(len(suits) > 1 for suits in board_by_ranks.values())

    if is_paired_board:
        # TODO: check for quads
        # TODO: check for full houses
        pass

    # TODO: check for regular flushes
    if flush_suit is not None:
        pass

    # TODO: check for straights
    possible_straights = get_possible_straights(ranks=[r for r, _ in board])
    if possible_straights:
        pass

    # TODO: check for three of a kind

    # TODO: check for two pairs
    # TODO: check for pairs
    # TODO: check for high cards

    return []
