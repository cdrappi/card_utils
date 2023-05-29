from itertools import chain, combinations
from typing import Dict, Iterator, List, Optional, Set, Tuple, TypeVar

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

    # one option is we simply make 0 melds
    candidates.append((get_deadwood(hand), [], hand))

    for n_combos in range(1, min(3, len(all_melds)) + 1):
        for melds in combinations(all_melds, n_combos):
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


def _get_set_layoffs(hand: List[Card], sets: List[str]) -> List[str]:
    """
    return list of cards that can be added to a set
    """
    rp = rank_partition(hand)
    return [f"{r}{rp[r][0]}" for r in sets if r in rp]


def _get_suit_run_layoffs(
    suit_ranks: List[str],
    suit_runs: List[Tuple[str, str]],
) -> List[List[str]]:
    if not suit_ranks:
        return []
    rank_set = set(suit_ranks)
    layoff_ranks = []
    for low, high in suit_runs:
        low_value = rank_to_value[low]
        high_value = rank_to_value[high]
        next_low = value_to_rank.get(low_value - 1)
        next_high = value_to_rank.get(high_value + 1)
        laid_off_low = []
        while next_low in rank_set:
            rank_set.remove(next_low)
            laid_off_low.append(next_low)
            low_value -= 1
            next_low = value_to_rank.get(low_value - 1)
        if laid_off_low:
            layoff_ranks.append(laid_off_low)

        laid_off_high = []
        while next_high in rank_set:
            rank_set.remove(next_high)
            laid_off_high.append(next_high)
            high_value += 1
            next_high = value_to_rank.get(high_value + 1)
        if laid_off_high:
            layoff_ranks.append(laid_off_high)
    return layoff_ranks


def _get_run_layoffs(
    hand: List[Card], runs: Dict[str, List[Tuple[str, str]]]
) -> List[List[str]]:
    """
    return map of suit to list of cards that can be added to a run
    """
    sp = suit_partition(hand)
    layoff_card_chunks: List[List[str]] = []
    for suit, suit_runs in runs.items():
        suit_chunks = _get_suit_run_layoffs(sp.get(suit, []), suit_runs)
        card_chunks = [[f"{suit}{r}" for r in sc] for sc in suit_chunks]
        layoff_card_chunks.extend(card_chunks)
    return layoff_card_chunks


T = TypeVar("T")


def powerset(s: List[T]) -> Iterator[List[T]]:
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def layoff_deadwood(
    hand: List[Card],
    opp_melds: List[List[Card]],
    stop_on_zero: bool = True,
) -> Tuple[int, List[List[Card]], List[Card], List[Card]]:
    """
    loop through all the possible ways we can
    meld our hand + lay off remaining cards
    """
    sets, runs = _split_sets_runs(opp_melds)
    candidates = []
    for _, melds, unmelded in get_candidate_melds(hand):
        sls = _get_set_layoffs(unmelded, sets)
        for set_layoffs in powerset(sls):
            lo_sets = [c for sl in set_layoffs for c in sl]
            um_set = set(unmelded) - set(lo_sets)
            rls = _get_run_layoffs(sorted(um_set), runs)
            for run_layoffs in powerset(rls):
                lo_runs = [c for rl in run_layoffs for c in rl]
                um_run = um_set - set(lo_runs)
                deadwood = get_deadwood(sorted(um_run))
                candidate = (
                    deadwood,
                    melds,
                    lo_sets + lo_runs,
                    sort_cards_by_rank(um_run),
                )
                if stop_on_zero and deadwood == 0:
                    return candidate
                candidates.append(candidate)
    return min(candidates)
