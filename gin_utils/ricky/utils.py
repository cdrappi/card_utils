import collections
import itertools
from typing import List, Tuple

from gin_utils.deal import new_game
from gin_utils.deck import rank_values, value_to_rank


def deal_new_game():
    """ shuffle up and deal each player 7 cards,
        put one card in the discard list,
        and put remaining cards in deck

    :return: (dict)
        {
            'p1_hand': [str],
            'p2_hand': [str],
            'discard': [str],
            'deck':    [str]
        }
    """
    return new_game(cards=7)


def sorted_hand_points(hand):
    """
    :param hand: ([str]) list of cards
    :return: ([str], int)
    """
    runs_3, runs_4 = get_runs(hand)
    sets_3, sets_4 = get_sets(hand)
    melds_3 = runs_3 + sets_3
    melds_4 = runs_4 + sets_4

    sorted_hand = sort_cards_by_rank(hand)
    hand_points_ = sum_points_by_ranks(hand)
    if len(hand) == 8:
        hand_points_ -= max(rank_values[r] for r, _ in hand)

    if len(melds_3 + melds_4) == 0:
        return sorted_hand, hand_points_

    for meld_3, meld_4 in itertools.product(melds_3, melds_4):
        cards_in_meld = {*meld_3, *meld_4}
        if len(cards_in_meld) == 7:
            # if there is a non-intersecting 3-meld and 4-meld,
            # then you have 0 points and win
            remaining_cards = list(set(hand) - set(cards_in_meld))
            return meld_4 + meld_3 + remaining_cards, 0

    for meld in melds_3 + melds_4:
        hand_without_meld = [card for card in hand if card not in meld]
        # print(hand, hand_without_meld, meld)
        meld_points = sum_points_by_ranks(hand_without_meld)
        if len(hand) == 8:
            meld_points -= max(rank_values[r] for r, _ in hand_without_meld)

        if meld_points < hand_points_:
            sorted_hand = meld + sort_cards_by_rank(hand_without_meld)
            hand_points_ = min(hand_points_, meld_points)

    return sorted_hand, hand_points_


def suit_partition(hand):
    """
    :param hand: ([str])
    :return: ({str: [str]} suit --> [ranks]
    """
    suit_to_ranks = collections.defaultdict(list)
    for rank, suit in hand:
        suit_to_ranks[suit].append(rank)

    return {
        suit: sorted(ranks, key=lambda r: rank_values[r])
        for suit, ranks in suit_to_ranks.items()
    }


def rank_partition(hand):
    """
    :param hand: ([str])
    :return: ({str: [str]} rank --> [suit]
    """
    rank_to_suits = collections.defaultdict(list)
    for rank, suit in hand:
        rank_to_suits[rank].append(suit)

    return dict(rank_to_suits)


def get_ranks_in_a_row(values, suit, n):
    """
    :param values: ([int])
    :param suit: (str)
    :param n: (int)
    :return: ([[str]])
    """
    runs = []
    if n == 3:
        for r0, r1, r2 in zip(values[0:-2], values[1:-1], values[2:]):
            # TODO: make this more efficient using
            if r0 == r1 - 1 == r2 - 2:
                runs.append([
                    f'{value_to_rank[r0]}{suit}',
                    f'{value_to_rank[r1]}{suit}',
                    f'{value_to_rank[r2]}{suit}',
                ])
    elif n == 4:
        for r0, r1, r2, r3 in zip(values[0:-3], values[1:-2], values[2:-1], values[3:]):
            if r0 == r1 - 1 == r2 - 2 == r3 - 3:
                runs.append([
                    f'{value_to_rank[r0]}{suit}',
                    f'{value_to_rank[r1]}{suit}',
                    f'{value_to_rank[r2]}{suit}',
                    f'{value_to_rank[r3]}{suit}',
                ])
    else:
        raise ValueError(
            f'get_ranks_in_a_row: n must be 3 or 4 (passed in n={n})'
        )


def get_runs_from_ranks(ranks, suit):
    """
    :param ranks: ([str])
    :param suit: (str)
    :return: ([[str]], [[str]])
    """
    runs_3, runs_4 = [], []

    if len(ranks) < 3:
        return runs_3, runs_4

    values = [rank_values[r] for r in ranks]
    if values[0] == 1:
        values.append(14)

    if len(values) >= 3:
        runs_3.extend(get_ranks_in_a_row(values, suit, 3))
    if len(values) >= 4:
        runs_4.extend(get_ranks_in_a_row(values, suit, 4))

    return runs_3, runs_4


def get_runs(hand):
    """
    :param hand: ([str])
    :return: ([[str]], [[str]])
    """
    suit_to_ranks = suit_partition(hand)
    runs_3, runs_4 = [], []
    for suit, ranks in suit_to_ranks.items():
        suit_runs_3, suit_runs_4 = get_runs_from_ranks(ranks, suit)
        runs_3.extend(suit_runs_3)
        runs_4.extend(suit_runs_4)
    return runs_3, runs_4


def get_sets(hand):
    """

    :param hand: ([str])
    :return: ([[str]], [[str]])
    """
    rank_to_suits = rank_partition(hand)
    sets_3, sets_4 = [], []
    for rank, suits in rank_to_suits.items():
        if len(suits) == 4:
            sets_4.append([f'{rank}{s}' for s in suits])
            sets_3.extend([
                [f'{rank}{s}' for s in suit_combo]
                for suit_combo in itertools.combinations(suits, 3)
            ])
        elif len(suits) == 3:
            sets_3.append([f'{rank}{s}' for s in suits])
    return sets_3, sets_4


def get_melds(hand) -> Tuple:
    """
    :param hand: ([str])
    :return: ([[str], [str]])
    """
    runs_3, runs_4 = get_runs(hand)
    sets_3, sets_4 = get_sets(hand)
    return runs_3 + sets_3, runs_4 + sets_4


def are_two_distinct_3_melds(melds_3: List[List]):
    """
    :param melds_3: ([[str]])
    :return: (bool)
    """
    if len(melds_3) < 2:
        return False

    for m1, m2 in itertools.combinations(melds_3, 2):
        if len({*m1, *m2}) == 6:
            return True

    return False


def sum_points_by_ranks(hand):
    """

    :param hand: ([str])
    :return: (int)
    """
    return sum(rank_values[r] for r, _ in hand)


def sort_cards_by_rank(cards):
    """
    :param cards: ([str])
    :return: ([str])
    """
    return sorted(cards, key=lambda c: rank_values[c[0]])


def sort_hand(hand):
    """
    :param hand: ([str])
    :return: ([str])
    """
    sorted_hand, _ = sorted_hand_points(hand)
    return sorted_hand


def hand_points(hand):
    """
    :param hand: ([str])
    :return: (int)
    """
    _, points = sorted_hand_points(hand)
    return points
