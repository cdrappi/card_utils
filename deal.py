import random

from deck import card_choices


def random_deck():
    """
    :return: ([str]) randomly shuffled deck of 52 cards
    """
    deck = [card for card, _ in card_choices]
    random.shuffle(deck)
    return deck


def new_game(cards=7):
    """ deal new game of gin

    :param cards: (int) how many cards to give to each player
    :return: (dict)
    """
    deck = random_deck()
    return {
        'p1_hand': deck[0:cards],
        'p2_hand': deck[cards:2 * cards],
        'discard': [deck[2 * cards]],
        'deck': deck[2 * cards + 1:],
    }
