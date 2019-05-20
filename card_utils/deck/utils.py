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


def ranks_to_sorted_values(ranks, aces_high, aces_low):
    """
    :param ranks: ([str])
    :param aces_high: (bool)
    :param aces_low: (bool)
    :return: ([int])
    """
    if not ranks:
        return []

    if not (aces_high or aces_low):
        raise ValueError(
            'Call to ranks_to_sorted_values: '
            'Aces cannot be neither high nor low! Makes no sense'
        )

    values = sorted(deck.rank_to_value[rank] for rank in ranks)
    if values[0] == deck.rank_to_value['A']:
        # if we have an ace...
        if aces_high:
            values.append(14)
        if not aces_low:
            # get rid of first card
            values.pop(0)

    return values
