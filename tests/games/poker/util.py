from card_utils.deck.utils import random_deck


def deal_random_board_hands(n_hands, n_cards):
    """ deal random n_hands of n_cards each,
        and a board of length 5

    :param n_hands: (int)
    :param n_cards: (int)
    :return: ([str], [[str]])
    """
    deck = random_deck()
    hands = [
        deck[n_cards * ii:n_cards * (ii + 1)]
        for ii in range(n_hands)
    ]
    board = deck[n_cards * n_hands:n_cards * n_hands + 5]
    return board, hands
