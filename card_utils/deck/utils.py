import random
from typing import List, Dict
from card_utils import deck
import time

Card = str


def random_deck() -> List[Card]:
    """
    :return: ([str]) randomly shuffled deck of 52 cards
    """
    deck_copy = [c for c in deck.cards]
    random.shuffle(deck_copy)
    return deck_copy


def rank_partition(cards) -> Dict[str, List[str]]:
    """
    :param cards: ([str])
    :return: ({str: [str]} rank --> [suit]
    """
    start = time.time()
    rank_to_suits: Dict[str, List[str]] = {}
    for rank, suit in cards:
        if rank not in rank_to_suits:
            rank_to_suits[rank] = []
        rank_to_suits[rank].append(suit)
    # print(
    #     f"python rank_partition took {(time.time() - start) * 1000000:.0f} micros"
    # )

    return rank_to_suits


def suit_partition(cards) -> Dict[str, List[str]]:
    """
    :param cards: ([str])
    :return: ({str: [str]} suit --> [ranks]
    """
    start = time.time()
    suit_to_ranks: Dict[str, List[str]] = {}
    for rank, suit in cards:
        if suit not in suit_to_ranks:
            suit_to_ranks[suit] = []
        suit_to_ranks[suit].append(rank)
    # print(
    #     f"python suit_partition took {(time.time() - start) * 1000000:.0f} micros"
    # )
    return suit_to_ranks


def ranks_to_sorted_values(
    ranks,
    aces_high,
    aces_low,
    distinct=False,
    reverse=False,
) -> List[int]:
    """
    :param ranks: ([str])
    :param aces_high: (bool)
    :param aces_low: (bool)
    :param distinct: (bool) if True, only return distinct values
    :param reverse: (bool) if True, sort in reverse order (high cards first)
    :return: ([int])
    """
    if not ranks:
        return []

    if not (aces_high or aces_low):
        raise ValueError(
            "Call to ranks_to_sorted_values: "
            "Aces cannot be neither high nor low! Makes no sense"
        )

    if distinct:
        ranks = set(ranks)

    values = []

    for rank in ranks:
        value = deck.ace_low_rank_to_value[rank]
        if value == deck.ace_low_rank_to_value["A"]:
            if aces_low:
                # 1
                values.append(deck.ace_low_rank_to_value["A"])
            if aces_high:
                # 14
                values.append(deck.ace_high_rank_to_value["A"])
        else:
            values.append(value)

    return sorted(values, reverse=reverse)
