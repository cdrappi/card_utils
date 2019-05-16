import itertools
from typing import List, Tuple

from gin_utils.deal import new_game
from gin_utils.deck import rank_values, value_to_rank, card_suits


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
    return new_game(n_cards=7)


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
    suit_to_ranks = {}
    for rank, suit in hand:
        if suit not in suit_to_ranks:
            suit_to_ranks[suit] = []
        suit_to_ranks[suit].append(rank)

    return suit_to_ranks


def rank_partition(hand):
    """
    :param hand: ([str])
    :return: ({str: [str]} rank --> [suit]
    """
    rank_to_suits = {}
    for rank, suit in hand:
        if rank not in rank_to_suits:
            rank_to_suits[rank] = []
        rank_to_suits[rank].append(suit)

    return rank_to_suits


def ranks_to_sorted_values(ranks, aces_high, aces_low):
    """
    :param ranks: ([str])
    :param aces_high: (bool)
    :param aces_low: (bool)
    :return: ([int])
    """
    if not (aces_high or aces_low):
        raise ValueError(
            'Call to ranks_to_sorted_values: '
            'Aces cannot be neither high nor low! Makes no sense'
        )

    values = sorted(rank_values[rank] for rank in ranks)
    # aces marked as low (1) now
    if values[0] == 1:
        # if we have an ace...
        if aces_high:
            values.append(14)
        if not aces_low:
            # get rid of first card
            values.pop(0)

    return values


def rank_straights(ranks, straight_length, aces_high=True, aces_low=True, suit=''):
    """
    :param ranks: ([str])
        e.g. ['A', '2', '7', 'T', 'J', 'Q', 'K']
    :param straight_length: (int) e.g. 5
    :param aces_high: (bool)
    :param aces_low: (bool)
    :param suit: (str) optional: inject a suit in the final returned value
    :return: ([[str]]) list of list of straights,
        each with length straight_length
        e.g. [['T','J','Q','K','A']]
        or [['Th', 'Jh', 'Qh', 'Kh', 'Ah']]
    """
    if len(ranks) < straight_length:
        # don't waste our time if its impossible to make a straight
        return []

    if suit not in {'', *card_suits}:
        raise ValueError(
            f'rank_straights: suit parameter must either be '
            f'the empty string "" or one of {card_suits}'
        )

    values = ranks_to_sorted_values(ranks, aces_high=aces_high, aces_low=aces_low)

    values_in_a_row = 0
    num_values = len(values)
    last_value = values[0]
    straights = []

    for ii, value in enumerate(values[1:]):
        if last_value + 1 == value:
            values_in_a_row += 1
        else:
            values_in_a_row = 0

        if values_in_a_row >= straight_length - 1:
            straights.append([
                f'{value_to_rank[v]}{suit}'
                for v in range(value - straight_length + 1, value + 1)
            ])

        if num_values + values_in_a_row < straight_length + ii:
            # exit early if there aren't enough cards left
            # to complete a straight
            return straights

        last_value = value

    return straights


def get_runs(hand):
    """ cleaner but slower (!?) method to get runs
    :param hand: ([str])
    :return: ([[str]], [[str]])
    """
    suit_to_ranks = suit_partition(hand)
    runs_3, runs_4 = [], []
    for suit, ranks in suit_to_ranks.items():
        runs_3.extend(rank_straights(ranks, 3, True, True, suit=suit))
        runs_4.extend(rank_straights(ranks, 4, True, True, suit=suit))
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
