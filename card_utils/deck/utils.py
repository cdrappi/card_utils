import copy
import random

from card_utils import deck


def random_deck():
    """
    :return: ([str]) randomly shuffled deck of 52 cards
    """
    deck_copy = copy.deepcopy(deck.cards)
    random.shuffle(deck_copy)
    return deck_copy


def rank_partition(cards):
    """
    :param cards: ([str])
    :return: ({str: [str]} rank --> [suit]
    """
    rank_to_suits = {}
    for rank, suit in cards:
        if rank not in rank_to_suits:
            rank_to_suits[rank] = []
        rank_to_suits[rank].append(suit)

    return rank_to_suits


def suit_partition(cards):
    """
    :param cards: ([str])
    :return: ({str: [str]} suit --> [ranks]
    """
    suit_to_ranks = {}
    for rank, suit in cards:
        if suit not in suit_to_ranks:
            suit_to_ranks[suit] = []
        suit_to_ranks[suit].append(rank)

    return suit_to_ranks


def ranks_to_sorted_values(ranks, aces_high, aces_low, reverse=False):
    """
    :param ranks: ([str])
    :param aces_high: (bool)
    :param aces_low: (bool)
    :param reverse: (bool) if True, sort in reverse order (high cards first)
    :return: ([int])
    """
    if not ranks:
        return []

    if not (aces_high or aces_low):
        raise ValueError(
            'Call to ranks_to_sorted_values: '
            'Aces cannot be neither high nor low! Makes no sense'
        )

    values = []
    for rank in ranks:
        value = deck.rank_to_value[rank]
        if value == deck.rank_to_value['A']:
            if aces_low:
                values.append(1)
            if aces_high:
                values.append(14)
        else:
            values.append(value)

    return sorted(values, reverse=reverse)
