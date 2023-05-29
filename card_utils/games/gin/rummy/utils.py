import copy
import itertools
from typing import Dict, List, Optional, Set, Tuple

from card_utils.deck import rank_to_value, value_to_rank
from card_utils.deck.utils import Card, rank_partition, suit_partition
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


def get_candidate_melds(
    hand: List[Card],
    max_deadwood: Optional[int] = None,
    stop_on_gin: bool = True,
) -> List[Tuple[int, List[List[Card]], List[str]]]:
    hand_set = set(hand)
    all_melds = _get_runs(hand) + _get_sets(hand)
    candidates: List[Tuple[int, List[List[Card]], List[Card]]] = []
    for n_combos in range(1, min(3, len(all_melds)) + 1):
        for melds in itertools.combinations(all_melds, n_combos):
            melded_cards = {c for m in melds for c in m}
            unique_cards = len(melded_cards)
            total_cards = sum(len(m) for m in melds)
            if unique_cards == total_cards:
                um_cards = sort_cards_by_rank(hand_set - melded_cards)
                deadwood = get_deadwood(um_cards)
                melds_list = [list(m) for m in melds]
                if deadwood == 0 and stop_on_gin:
                    # they made gin, so return early
                    return [(0, melds_list, [])]
                if max_deadwood is None or deadwood <= max_deadwood:
                    candidates.append((deadwood, melds_list, um_cards))
    return candidates


def split_melds(
    hand: List[str],
    melds: Optional[List[List[Card]]] = None,
) -> Tuple[int, List[List[str]], List[str]]:
    if melds is not None:
        hand_set = set(hand)
        # they pick their melds to knock
        melded_cards = {c for m in melds for c in m}
        um_cards = sort_cards_by_rank(hand_set - melded_cards)
        return get_deadwood(um_cards), melds, sort_cards_by_rank(um_cards)

    candidates = get_candidate_melds(hand, stop_on_gin=True)
    return min(candidates)


def _split_sets_runs(
    melds: List[List[Card]],
) -> Tuple[List[str], Dict[str, List[Tuple[str, str]]]]:
    """
    return tuple where:
    -> first element is a list of all the ranks in the 3-sets
    -> second element is map of suit to tuple of min/max rank in run
    """
    runs: Dict[str, List[Tuple[str, str]]]
    sets, runs = [], {}
    for meld in melds:
        sp = suit_partition(meld)
        rp = rank_partition(meld)
        if len(sp) == 1:
            [(suit, ranks)] = sp.items()
            if suit not in runs:
                runs[suit] = []
            runs[suit].append((ranks[0], ranks[-1]))
        elif len(rp) == 1:
            [(rank, suits)] = rp.items()
            if len(suits) == 3:
                # if they have all 4 of the rank,
                # then opponent can't possibly lay off
                sets.append(rank)
        else:
            raise ValueError(f"invalid meld: {meld}")
    return sorted(sets), runs


def _get_set_layoffs(hand: List[Card], sets: List[str]) -> Set[str]:
    """
    return list of cards that can be added to a set
    """
    rp = rank_partition(hand)
    return {f"{s}{rp[s][0]}" for s in sets if s in rp}


def _get_suit_run_layoffs(
    suit_ranks: List[str],
    suit_runs: List[Tuple[str, str]],
) -> List[str]:
    if not suit_ranks:
        return []
    rank_set = set(suit_ranks)
    laid_off = []
    for low, high in suit_runs:
        low_value = rank_to_value[low]
        high_value = rank_to_value[high]
        next_low = value_to_rank.get(low_value - 1)
        next_high = value_to_rank.get(high_value + 1)
        while next_low in rank_set:
            rank_set.remove(next_low)
            laid_off.append(next_low)
            low_value -= 1
            next_low = value_to_rank.get(low_value - 1)
        while next_high in rank_set:
            rank_set.remove(next_high)
            laid_off.append(next_high)
            high_value += 1
            next_high = value_to_rank.get(high_value + 1)
    return laid_off


def _get_run_layoffs(
    hand: List[Card], runs: Dict[str, List[Tuple[str, str]]]
) -> Dict[str, List[str]]:
    """
    return map of suit to list of cards that can be added to a run
    """
    sp = suit_partition(hand)
    return {
        suit: _get_suit_run_layoffs(sp.get(suit, []), suit_runs)
        for suit, suit_runs in runs.items()
    }


def layoff_deadwood(
    hand: List[Card],
    opp_melds: List[List[Card]],
) -> Tuple[int, List[List[Card]], List[Card]]:
    """
    1. split the opponent melds into runs and sets
    2. for each set, see if there are cards we can add to it
    """
    sets, runs = _split_sets_runs(opp_melds)
    set_layoffs = _get_set_layoffs(hand, sets)
    run_layoffs = _get_run_layoffs(hand, runs)

    return (0, [], [])
