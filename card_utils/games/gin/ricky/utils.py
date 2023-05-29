import itertools
from typing import Iterable, List, Tuple

from card_utils import deck
from card_utils.deck.utils import suit_partition
from card_utils.games.gin.utils import get_sets, new_game, rank_straights


def deal_new_game():
    """shuffle up and deal each player 7 cards,
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


def sorted_hand_points(hand) -> Tuple[List[str], int]:
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
        hand_points_ -= max(deck.rank_to_value[r] for r, _ in hand)

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
            meld_points -= max(
                deck.rank_to_value[r] for r, _ in hand_without_meld
            )

        if meld_points < hand_points_:
            sorted_hand = meld + sort_cards_by_rank(hand_without_meld)
            hand_points_ = min(hand_points_, meld_points)

    return sorted_hand, hand_points_


def get_runs(hand):
    """cleaner but slower (!?) method to get runs
    :param hand: ([str])
    :return: ([[str]], [[str]])
    """
    suit_to_ranks = suit_partition(hand)
    runs_3, runs_4 = [], []
    for suit, ranks in suit_to_ranks.items():
        runs_3.extend(rank_straights(ranks, 3, 3, True, True, suit=suit))
        runs_4.extend(rank_straights(ranks, 4, 4, True, True, suit=suit))
    return runs_3, runs_4


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
    return sum(deck.rank_to_value[r] for r, _ in hand)


def sort_cards_by_rank(cards: Iterable[str]):
    """
    :param cards: ([str])
    :return: ([str])
    """
    return sorted(cards, key=lambda c: deck.rank_to_value[c[0]])


def sort_hand(hand) -> List[str]:
    """
    :param hand: ([str])
    :return: ([str])
    """
    sorted_hand, _ = sorted_hand_points(hand)
    return sorted_hand


def hand_points(hand: List[str]) -> int:
    """
    :param hand: ([str])
    :return: (int)
    """
    _, points = sorted_hand_points(hand)
    return points
