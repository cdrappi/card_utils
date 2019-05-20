""" util functions for omaha games """
import collections
from typing import Tuple

from card_utils.deck import ace_high_rank_to_value
from card_utils.deck.utils import (
    rank_partition,
    suit_partition,
    ranks_to_sorted_values,
)
from card_utils.games.poker import (
    hand_order,
    STRAIGHT_FLUSH,
    QUADS,
    FULL_HOUSE,
    FLUSH,
    STRAIGHT,
    THREE_OF_A_KIND,
    TWO_PAIR,
    ONE_PAIR,
    HIGH_CARD,
)


def _validate_board(board):
    """ raise exception if board doesn't have exactly 5 cards
    :param board: (set(str)) set of 5 cards
    :return:
    """
    if len(board) != 5:
        raise ValueError(
            f'omaha.utils.get_best_hand: '
            f'board must have 5 cards\n'
            f'input: {board}'
        )


def _validate_hand(hand):
    """ raise exception if all hands don't have exactly 4 cards

    :param hand: (set(str)) set of 4 cards
    :return: None
    """
    if len(hand) != 4:
        raise ValueError(
            f'omaha.utils._validate_hands: '
            f'all hands must have 4 cards\n'
            f'invalid hand: {hand}'
        )


def _get_suit_with_gte_3_cards(board_by_suits):
    for suit, ranks in board_by_suits.items():
        if len(ranks) >= 3:
            return suit

    return None


def _get_highest_except(values, excluded_values):
    """
    :param values: ([int])
    :param excluded_values: (set(int))
    :return: (int) highest value in values except the excluded value
    """
    return max(set(values).difference(excluded_values))


def _get_connecting_values(v1, v2, v3):
    """ get tuples of card values that could make a straight
        given cards with values v1, v2, v3 are on the board

    :param v1: (int)
    :param v2: (int)
    :param v3: (int)
    :return: (set(tuple(int))) set of tuples of ints
    """
    if len({v3, v2, v1}) < 3:
        # can't make a straight without 3 distinct values
        return set()

    n_gaps = v3 - v1 - 2
    if n_gaps > 2:
        # can't make a straight if there are 3+ gaps
        # e.g. 4-GAP-6-GAP-GAP-9
        return set()

    cards_on_board = {v1, v2, v3}

    # worst straight is the wheel A-2-3-4-5
    worst_straight_start = max(1, v1 + n_gaps - 2)
    # best straight is broadway T-J-Q-K-A
    best_straight_start = min(10, v1 - n_gaps + 2)

    print(cards_on_board, worst_straight_start, best_straight_start)

    connecting_values = set()
    for bottom_value in range(worst_straight_start, best_straight_start + 1):
        straight_values = set(range(bottom_value, bottom_value + 5))
        values_to_make_straight = straight_values.difference(cards_on_board)
        connecting_values.add(tuple(sorted(values_to_make_straight)))

    return connecting_values


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


def get_best_straight(possible_straights, hand):
    """ get list of indices of hands that make the strongest straight
        if no one makes a straight, return empty list

    :param possible_straights: ({tuple(str): int})
        map tuple of connecting cards --> best straight value they make
    :param hand: (set(str)) set of strings
    :return: (int) top value in the straight, or 0 if no straight
    """
    highest_straight_value = 0  # e.g. 14 for broadway, 5 for the wheel
    hand_values = set(
        ranks_to_sorted_values(
            ranks=[r for r, _ in hand],
            aces_high=True,
            aces_low=True
        )
    )
    for connecting_values, max_value in possible_straights.items():
        connecting_cards = set(connecting_values) & hand_values
        if len(connecting_cards) == 2:
            # we've made a straight!
            if max_value > highest_straight_value:
                highest_straight_value = max_value

    return highest_straight_value


def get_best_flush(hand_flush_values):
    """ get indexes of hands that make the best flush
        in omaha, only one hand can make the same flush,
        since you must play exactly two cards from your hand.
        still, we return a list to keep the return type
        consistent with other functions

    :param hand_flush_values: ([set(int)]
    :return: (int|None) top value in the flush, or 0 if no flush
    """
    highest_flush_value = 0
    if len(hand_flush_values) >= 2:
        max_flush_value = max(hand_flush_values)
        if max_flush_value > highest_flush_value:
            highest_flush_value = max_flush_value

    return highest_flush_value


def get_best_quads(hands_values, board_values):
    """
    :param hands_values: (collections.Counter({int: int}))
    :param board_values: (collections.Counter({int: int}))
    :return: (int, int) quads value, kicker
    """
    best_quads = tuple()

    for board_value, board_ct in board_values.items():
        # only 2 ways to make quads:
        if board_ct == 2 and hands_values[board_value] == 2:
            best_kicker = _get_highest_except(board_values, {board_value})
            quads = (board_value, best_kicker)
            if quads > best_quads:
                best_quads = quads
        elif board_ct == 3 and hands_values[board_value] == 1:
            best_kicker = _get_highest_except(hands_values, {board_value})
            quads = (board_value, best_kicker)
            if quads > best_quads:
                best_quads = quads

    return best_quads


def get_best_full_house(hands_values, board_values):
    """
    :param hands_values: (collections.Counter({int: int}))
    :param board_values: (collections.Counter({int: int}))
    :return: (int, int) trips value, pair value
    """
    best_boat = tuple()  # "boat" is another term for full house

    for board_value, board_ct in board_values.items():
        if board_ct == 3:
            # if there are three of a kind on the board,
            # then we have a full house if there is a pair in our hand
            for hand_value, hand_ct in hands_values.items():
                if hand_ct == 2:
                    boat = (board_value, hand_value)
                    if boat > best_boat:
                        best_boat = boat

        elif board_ct == 2:
            # if the board is paired:
            for hand_value, hand_ct in hands_values.items():
                if hand_ct >= 2 and board_values[hand_value] == 1:
                    # first look for pairs in the hand
                    # that also have 1 card on the board
                    boat = (hand_value, board_value)
                    if boat > best_boat:
                        best_boat = boat

            if hands_values[board_value] == 1:
                # if we have one of the pair cards on the board,
                # see if we have any other pairs,
                # making a boat the hard way
                other_pairs = [
                    hand_value
                    for hand_value, hand_count in hands_values.items()
                    if bool(
                        hand_value != board_value
                        and board_values[hand_value] >= 1
                    )
                ]
                for hv in other_pairs:
                    boat = (board_value, hv)
                    if boat > best_boat:
                        best_boat = boat

    return best_boat


def get_best_three_of_a_kind(hand_values, board_values):
    """
    :param hand_values: (collections.Counter({int: int}))
    :param board_values: (collections.Counter({int: int}))
    :return: (int, int, int) trips value, best kicker, 2nd best kicker
    """
    best_three_of_a_kind = tuple()

    for board_value, board_ct in board_values.items():
        # there can be three of a kind on the board
        if board_ct == 3:
            # in this case, the hand's biggest 2 kickers play
            # if they have 2+ distinct cards
            # (e.g. if they have quads in their hand,
            #       then they have a full house,
            #       which would have returned
            #       before this function was called)
            if len(set(hand_values).difference({board_value})) >= 2:
                k_1 = _get_highest_except(hand_values, {board_value})
                k_2 = _get_highest_except(hand_values, {board_value, k_1})
                three_of_a_kind = (board_value, k_1, k_2)
                if three_of_a_kind > best_three_of_a_kind:
                    best_three_of_a_kind = three_of_a_kind

        # or a paired board, and the hand can make trips
        elif board_ct == 2:
            # if the board is paired, search for cases where
            # the player has this paired card in their hand once
            if hand_values[board_value] == 1:
                # the player's 5-card omaha hand is then
                # the trips, plus the best kicker from the hand
                # and the best kicker from the board
                k_1 = _get_highest_except(
                    values=set(board_values).union(hand_values),
                    excluded_values={board_value}
                )
                if k_1 in board_values and k_1 not in hand_values:
                    # then k_2 has to come from the hand
                    k_2 = _get_highest_except(hand_values, {board_value})
                elif k_1 in hand_values and k_1 not in board_values:
                    # then k_2 has to come from the hand
                    k_2 = _get_highest_except(board_values, {board_value})
                else:
                    # the player would have a full house,
                    # so we should never get here unless calling
                    # get_best_three_of_a_kind directly
                    # however, we then choose the 2nd best kicker
                    # from either board or hand
                    k_2 = _get_highest_except(
                        values=set(board_values).union(hand_values),
                        excluded_values={board_value, k_1}
                    )
                three_of_a_kind = (board_value, k_1, k_2)
                if three_of_a_kind > best_three_of_a_kind:
                    best_three_of_a_kind = three_of_a_kind

        # or can have a set
        elif board_ct == 1:
            if hand_values[board_value] >= 2 and len(board_values) >= 3:
                # we have a set,
                # AND there are at least 3 distinct cards on the board
                # if there are not, then we would have made a full house,
                # our set + two of the quads on the board,
                # and this is not three-of-a-kind, but much better.
                k_1 = _get_highest_except(board_values, {board_value})
                k_2 = _get_highest_except(board_values, {board_value, k_1})
                three_of_a_kind = (board_value, k_1, k_2)
                if three_of_a_kind > best_three_of_a_kind:
                    best_three_of_a_kind = three_of_a_kind

    return best_three_of_a_kind


def get_best_two_pair(hand_values, board_values):
    """
    :param hand_values: (collections.Counter({int: int}))
    :param board_values: (collections.Counter({int: int}))
    :return: (int, int, int) top pair, bottom pair, kicker
    """
    best_two_pair = tuple()

    pairs_on_board = set(bv for bv, bc in board_values.items() if bc >= 2)
    pairs_in_hand = set(hv for hv, hc in hand_values.items() if hc >= 2)
    if pairs_on_board and pairs_in_hand:
        # if the board has a pair and our hand has a different pair,
        # we have a two pair, and we can now figure out the best one
        pairs_in_union = pairs_on_board | pairs_in_hand
        top_pair = max(pairs_in_union)
        second_pair = _get_highest_except(pairs_in_union, {top_pair})
        kicker = _get_highest_except(board_values, {top_pair, second_pair})
        best_two_pair = (top_pair, second_pair, kicker)

    if pairs_on_board:
        # TODO
        # next case: our board can have a pair, and
        # our hand can make a pair connecting with the board
        pass

    common_cards = set(board_values) & set(hand_values)
    if len(common_cards) >= 2:
        # we have 2 pair!
        # TODO
        pass

    return best_two_pair


def get_best_pair(hand_values, board_values):
    """
    :param hand_values: (collections.Counter({int: int}))
    :param board_values: (collections.Counter({int: int}))
    :return: (int, int, int, int) pair, best kicker, 2nd best, 3rd best
    """
    best_pair = tuple()

    # TODO
    return best_pair


def get_hand_strength(board, hand) -> Tuple:
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


    :param board: (set(str)) set of 5 cards
    :param hand: (set(str)) set of 4 cards
    :return: (tuple)
    """
    _validate_board(board)
    _validate_hand(hand)

    board_by_suits = suit_partition(board)
    flush_suit = _get_suit_with_gte_3_cards(board_by_suits)

    # Check to see if anyone has a straight flush
    if flush_suit is not None:
        possible_straight_flushes = get_possible_straights(
            ranks=board_by_suits[flush_suit]
        )
        if possible_straight_flushes:
            best_straight_flush = get_best_straight(
                possible_straights=possible_straight_flushes,
                # filter hands by suit, and then we can use the
                # same function for straight flushes
                # as we use for straights
                hand=set(f'{r}{s}' for r, s in hand if s == flush_suit)
            )
            if best_straight_flush:
                return hand_order[STRAIGHT_FLUSH], best_straight_flush

    # If the board is paired, we could have quads or a full house
    board_by_ranks = rank_partition(board)
    is_paired_board = any(len(suits) > 1 for suits in board_by_ranks.values())

    hand_values_list = [ace_high_rank_to_value[r] for r, _ in hand]

    hand_values = collections.Counter(hand_values_list)
    board_values = collections.Counter({
        ace_high_rank_to_value[rank]: len(suits)
        for rank, suits in board_by_ranks.items()
    })

    if is_paired_board:
        best_quads = get_best_quads(hand_values, board_values)
        if best_quads:
            return hand_order[QUADS], best_quads

        best_full_houses = get_best_full_house(hand_values, board_values)
        if best_full_houses:
            return hand_order[FULL_HOUSE], best_full_houses

    if flush_suit is not None:
        best_flush = get_best_flush(
            hand_flush_values=set(
                ace_high_rank_to_value[r]
                for r, s in hand
                if s == flush_suit
            )
        )
        if best_flush:
            return hand_order[FLUSH], best_flush

    possible_straights = get_possible_straights([r for r, _ in board])
    if possible_straights:
        best_straight = get_best_straight(
            possible_straights=possible_straights,
            hand=hand
        )
        if best_straight:
            return hand_order[STRAIGHT], best_straight

    best_three_of_a_kind = get_best_three_of_a_kind(hand_values, board_values)
    if best_three_of_a_kind:
        return (hand_order[THREE_OF_A_KIND], *best_three_of_a_kind)

    best_two_pair = get_best_two_pair(hand_values, board_values)
    if best_two_pair:
        return (hand_order[TWO_PAIR], *best_two_pair)

    best_pair = get_best_pair(hand_values, board_values)
    if best_pair:
        return (hand_order[ONE_PAIR], *best_pair)

    return (hand_order[HIGH_CARD], *hand_values)


def get_best_hand(board, hands):
    """ get the index of the best omaha hand given a board

    :param board: ([str]) list of 5 cards
    :param hands: ([set(str)]) list of sets of 4 cards
    :return: ([int]) indices of `hands` that makes the strongest omaha hand,
        --> this is a list because it is possible to "chop" with
            every hand rank except straight flushes, quads and flushes
    """
    return max(
        range(len(hands)),
        key=lambda ii: get_hand_strength(board, hands[ii])
    )


""" fin """
