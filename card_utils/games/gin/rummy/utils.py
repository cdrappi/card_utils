import itertools

from typing import List, Set, Tuple

from card_utils.deck import rank_to_value
from card_utils.deck.utils import Card, suit_partition
from card_utils.games.gin.ricky.utils import rank_straights, sort_cards_by_rank
from card_utils.games.gin.utils import get_sets, new_game


def deal_new_game():
    """shuffle up and deal each player 10 cards,
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
    return new_game(n_cards=10)


def _get_runs(hand: List[str]) -> List[Set[str]]:
    sp = suit_partition(hand)
    runs_map = {
        suit: rank_straights(
            ranks,
            suit=suit,
            aces_high=True,
            aces_low=True,
        )
        for suit, ranks in sp.items()
    }
    return [set(run) for _, runs in runs_map.items() for run in runs]


def _get_sets(hand: List[str]) -> List[Set[str]]:
    sets_3, sets_4 = get_sets(hand)
    return [set(s) for s in sets_3 + sets_4]


def get_deadwood(unmelded_cards: List[Card]):
    """get the deadwood points of a hand

    :param unmelded_cards: ([str]) list of cards
    :return: (int) deadwood points
    """
    return sum(min(10, rank_to_value[c[0]]) for c in unmelded_cards)


def split_melds(hand: List[str]) -> Tuple[List[List[str]], List[str], int]:
    hand_set = set(hand)
    all_melds = _get_runs(hand) + _get_sets(hand)
    candidates: List[Tuple[List[List[str]], List[str], int]] = []
    for n_combos in range(1, min(3, len(all_melds)) + 1):
        for melds in itertools.combinations(all_melds, n_combos):
            melded_cards = {c for m in melds for c in m}
            unique_cards = len(melded_cards)
            total_cards = sum(len(m) for m in melds)
            if unique_cards == total_cards:
                um_cards = sort_cards_by_rank(hand_set - melded_cards)
                deadwood = get_deadwood(um_cards)
                melds_list = [list(m) for m in melds]
                if deadwood == 0:
                    # they made gin
                    return melds_list, [], 0
                candidates.append((melds_list, um_cards, deadwood))
    return min(candidates, key=lambda x: x[2])
