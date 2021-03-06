""" brute force hand ranks for holdem
    where everyone plays the best 5 card hand
"""

import itertools

from card_utils.games.poker.five_card_hand_rank import five_card_hand_rank
from card_utils.games.poker.util import get_best_hands_generic


def brute_force_holdem_rank(board, hand):
    """
    :param board: ([str]) 5 board cards
    :param hand: ([str]) 4 hole cards
    :return: ([str], tuple) list of five card hand, and its tuple-rank
        a combo of 3 board cards and 2 hole cards
    """
    all_seven_cards = [*board, *hand]
    possible_combinations = itertools.combinations(all_seven_cards, 5)
    best_hand = max(possible_combinations, key=five_card_hand_rank)
    return five_card_hand_rank(best_hand)


def get_best_hands_brute_force(board, hands):
    """ get the index of the best holdem hand given a board

    :param board: ([str]) list of 5 cards
    :param hands: ([set(str)]) list of sets of 4 cards
    :return: ([[int]]) indices of `hands` that makes the strongest holdem hand,
        --> this is a list because it is possible to "chop" with
            every hand rank as everyone can play the board
    """
    return get_best_hands_generic(
        hand_strength_function=brute_force_holdem_rank,
        board=board,
        hands=hands,
    )
