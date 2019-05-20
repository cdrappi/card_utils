from card_utils.games.poker import (
    inverse_hand_order
)


def pretty_hand_rank(hand_rank_tuple):
    """
    :param hand_rank_tuple: (tuple(int))
    :return: (str)
    """
    hand_order_, *kickers_ = hand_rank_tuple
    return inverse_hand_order[hand_order_]
