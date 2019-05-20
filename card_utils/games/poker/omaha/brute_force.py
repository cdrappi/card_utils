""" brute force hand ranks for testing a faster, omaha-optimised function """

import itertools

from card_utils.games.poker.five_card_hand_rank import five_card_hand_rank


def brute_force_omaha_hi_rank(board, hand):
    """
    :param board: ([str]) 5 board cards
    :param hand: ([str]) 4 hole cards
    :return: ([str], tuple) list of five card hand, and its tuple-rank
        a combo of 3 board cards and 2 hole cards
    """
    possible_combinations = (
        list(board_cards) + list(hole_cards)
        for board_cards in itertools.combinations(board, 3)
        for hole_cards in itertools.combinations(hand, 2)
    )
    best_hand = max(possible_combinations, key=five_card_hand_rank)
    return five_card_hand_rank(best_hand)


def get_best_hand_brute_force(board, hands):
    """ get the index of the best omaha hand given a board

    :param board: ([str]) list of 5 cards
    :param hands: ([set(str)]) list of sets of 4 cards
    :return: ([int]) indices of `hands` that makes the strongest omaha hand,
        --> this is a list because it is possible to "chop" with
            every hand rank except straight flushes, quads and flushes
    """
    return max(
        range(len(hands)),
        key=lambda ii: brute_force_omaha_hi_rank(board, hands[ii])
    )