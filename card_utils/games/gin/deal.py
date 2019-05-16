from card_utils import deck
from card_utils.deck.utils import random_deck


def new_game(n_cards):
    """ deal new game of gin

    :param n_cards: (int) how many cards to give to each player
    :return: (dict)
    """
    if 2 * n_cards + 1 >= len(deck.cards):
        raise ValueError(
            f'gin.deal.new_game: too many cards ({n_cards}), '
            f'not enough to deal a game to two players!'
        )

    deck_ = random_deck()
    return {
        'p1_hand': deck_[0:n_cards],
        'p2_hand': deck_[n_cards:2 * n_cards],
        'discard': [deck_[2 * n_cards]],
        'deck': deck_[2 * n_cards + 1:],
    }
