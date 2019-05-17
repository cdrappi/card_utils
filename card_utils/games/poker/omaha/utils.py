""" util functions for omaha games """
import collections

from card_utils.deck import value_to_rank, ace_high_rank_to_value
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


def _get_connecting_values(v1, v2, v3):
    """ get tuples of card values that could make a straight
        given cards with values v1, v2, v3 are on the board

    :param v1: (int)
    :param v2: (int)
    :param v3: (int)
    :return: (set(tuple(int))) set of tuples of ints
    """
    n_gaps = v3 - v1 - 1
    if n_gaps > 2:
        # can't make a straight if there are 3+ gaps
        # e.g. 5-GAP-6-GAP-GAP-9
        return set()

    cards_on_board = {v1, v2, v3}
    worst_straight_start = max(1, v1 + n_gaps - 2)
    best_straight_start = min(14, v1 - n_gaps + 2)

    straight_values = set()
    for bottom_value in range(worst_straight_start, best_straight_start):
        straight_values = set(range(bottom_value, bottom_value + 5))
        values_to_make_straight = straight_values.difference(cards_on_board)
        straight_values.add(tuple(values_to_make_straight))

    return straight_values


def get_possible_straights(ranks):
    """ get a list of hole card combinations
        that could make a straight
        on a board with these ranks

    :param ranks: ([str])
    :return: ({tuple(int): int})
        map connecting card values to list of values
        to the highest value straight they'd make
    """
    if len(ranks) < 3:
        # need 3 cards to make a straight
        return {}

    values = ranks_to_sorted_values(
        ranks=ranks,
        aces_high=True,
        aces_low=True
    )

    connecting_values = {}
    for v1, v2, v3 in zip(values[0:-2], values[1:-1], values[2:]):
        connectors_set = _get_connecting_values(v1, v2, v3)
        for connectors in connectors_set:
            highest_straight_value = max({v3, *connectors})
            if connectors not in connecting_values:
                connecting_values[connectors] = highest_straight_value
            elif highest_straight_value > connecting_values[connectors]:
                connecting_values[connectors] = highest_straight_value

    return connecting_values


def get_possible_straight_flushes(ranks, suit):
    """ get a list of possible hole cards that could make straight flushes
        if we have these ranks on the board in this suit

    :param ranks: ([str]) e.g. ['J', 'Q', 'K']
    :param suit: (str) e.g. 'c'
    :return: ([tuple(str): int]) e.g. {('9c', 'Tc'): 13, ('Tc', 'Ac'): 14}
        list of sets of strings
    """
    return {
        tuple(f'{value_to_rank[v]}{suit}' for v in connectors): max_value
        for connectors, max_value in get_possible_straights(ranks)
    }


def get_best_straights(possible_straights, hands):
    """ get list of indices of hands that make the strongest straight
        if no one makes a straight, return empty list

    :param possible_straights: ({tuple(str): int})
        map tuple of connecting cards --> best straight value they make
    :param hands: ([[str]] list of list of strings
    :return: ([int]) list of indices of hands that make the best straight
        empty list if no one makes best straight
    """
    best_straight_indices = []
    best_straight_highest_value = 0  # e.g. 14 for broadway, 5 for the wheel
    for ii, hand in enumerate(hands):
        hand_values = set(
            ranks_to_sorted_values(
                ranks=[r for r, _ in hand],
                aces_high=True,
                aces_low=True
            )
        )
        for connecting_values, max_value in possible_straights.items():
            connecting_cards = set(connecting_values).union(hand_values)
            if len(connecting_cards) == 2:
                # we've made a straight!
                if max_value > best_straight_highest_value:
                    best_straight_highest_value = max_value
                    best_straight_indices = [ii]
                elif max_value == best_straight_highest_value:
                    best_straight_indices.append(ii)

    return best_straight_indices


def get_best_flushes(hands_flush_values):
    """ get indexes of hands that make the best flush
        in omaha, only one hand can make the same flush,
        since you must play exactly two cards from your hand.
        still, we return a list to keep the return type
        consistent with other functions

    :param hands_flush_values: ([set(int)]
    :return: ([int])
    """
    best_flush_indices = []
    best_flush_highest_value = 0
    for ii, hand_flush_values in enumerate(hands_flush_values):
        if len(hand_flush_values) >= 2:
            max_flush_value = max(hand_flush_values)
            if max_flush_value == best_flush_highest_value:
                raise ValueError(
                    f'Two Omaha hands cannot make the same strength flush!'
                )
            if max_flush_value > best_flush_highest_value:
                best_flush_indices = [ii]
                best_flush_highest_value = max_flush_value

    return best_flush_indices


def get_best_quads(hands_values, board_values):
    """
    :param hands_values: ([[int]])
    :param board_values:
    :return:
    """
    # TODO: check for quads
    best_quad_indices = []

    return best_quad_indices


def get_best_full_houses(hands_values, board_values):
    """
    :param hands_values:
    :param board_values:
    :return:
    """
    # TODO: check for full houses
    best_full_house_indices = []

    return best_full_house_indices


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
    :param hands: ([set(str)]) list of sets of 4 cards
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
        possible_straight_flushes = get_possible_straights(
            ranks=board_by_suits[flush_suit]
        )
        if possible_straight_flushes:
            best_straight_flushes = get_best_straights(
                possible_straights=possible_straight_flushes,
                hands=[
                    # filter hands by suit, and then we can use the
                    # same function for straight flushes
                    # as we use for straights
                    set(f'{r}{s}' for r, s in hand if s == flush_suit)
                    for hand in hands
                ],
            )
            if best_straight_flushes:
                return best_straight_flushes

    # If the board is paired, we could have quads or a full house
    board_by_ranks = rank_partition(board)
    is_paired_board = any(len(suits) > 1 for suits in board_by_ranks.values())

    if is_paired_board:
        hands_values = [
            dict(collections.Counter(ace_high_rank_to_value[r] for r, _ in hand))
            for hand in hands
        ]
        board_values = {
            ace_high_rank_to_value[rank]: len(suits)
            for rank, suits in board_by_ranks.items()
        }
        best_quads = get_best_quads(hands_values, board_values)
        if best_quads:
            return best_quads

        best_full_houses = get_best_full_houses(hands_values, board_values)
        if best_full_houses:
            return best_full_houses

    if flush_suit is not None:
        best_flushes = get_best_flushes(
            hands_flush_values=[
                set(
                    ace_high_rank_to_value[r]
                    for r, s in hand
                    if s == flush_suit
                )
                for hand in hands
            ]
        )
        if best_flushes:
            return best_flushes

    possible_straights = get_possible_straights([r for r, _ in board])
    if possible_straights:
        best_straights = get_best_straights(
            possible_straights=possible_straights,
            hands=hands
        )
        if best_straights:
            return best_straights

    # TODO: check for three of a kind

    # TODO: check for two pairs
    # TODO: check for pairs
    # TODO: check for high cards

    return []
