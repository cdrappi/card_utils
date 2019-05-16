from card_utils import deck
from card_utils.deck.utils import random_deck


def new_game(cards):
    """ deal new game of gin

    :param cards: (int) how many cards to give to each player
    :return: (dict)
    """
    if 2 * cards + 1 >= len(deck.cards):
        raise ValueError(
            f'gin.deal.new_game: too many cards, '
            f'cannot exceed ~2x deck length!'
        )

    deck_ = random_deck()
    return {
        'p1_hand': deck_[0:cards],
        'p2_hand': deck_[cards:2 * cards],
        'discard': [deck_[2 * cards]],
        'deck': deck_[2 * cards + 1:],
    }
