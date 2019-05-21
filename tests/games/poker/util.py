from card_utils.games.poker.util import deal_random_hands


def deal_random_board_hands(n_hands, n_cards):
    """ deal random n_hands of n_cards each,
        and a board of length 5

    :param n_hands: (int)
    :param n_cards: (int)
    :return: ([str], [[str]])
    """
    remaining_deck, hands = deal_random_hands(n_hands, n_cards)
    board = remaining_deck[0:5]
    return board, hands
