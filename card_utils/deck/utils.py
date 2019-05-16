import copy
import random

from card_utils.deck import cards


def random_deck():
    """
    :return: ([str]) randomly shuffled deck of 52 cards
    """
    deck = copy.deepcopy(cards)
    random.shuffle(deck)
    return deck
