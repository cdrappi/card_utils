""" util functions for holdem games

the only functions here that you'll want to call are:

The only two functions you'll want to call are:

>>> get_hand_strength_fast(board, hand)
    --> returns a tuple of varying length,
        representing hand-strength

and

>>> get_best_hands_fast(board, hands)
    --> returns the indices in `hands` that make
        the strongest 5-card holdem hand

Example inputs:

board  = ['3c', 'Qh', 'Kd', '2s', '7h']
hand_1 = ['Ah', 'Td']
hand_2 = ['5s', '2h']
hands  = [hand_1, hand_2]
"""
import itertools
from typing import Dict, List, Optional, Tuple

from card_utils.deck import ace_high_rank_to_value
from card_utils.deck.utils import (
    rank_partition,
    ranks_to_sorted_values,
    suit_partition,
)
from card_utils.games.poker import (
    FLUSH,
    FULL_HOUSE,
    HIGH_CARD,
    ONE_PAIR,
    QUADS,
    STRAIGHT,
    STRAIGHT_FLUSH,
    THREE_OF_A_KIND,
    TWO_PAIR,
    hand_order,
)
from card_utils.games.poker.community.holdem.brute_force import (
    brute_force_holdem_rank,
)
from card_utils.games.poker.community.utils import simulate_all_in_equity
from card_utils.games.poker.util import get_best_hands_generic
from card_utils.util import LightDefaultDict, count_items


def sim_holdem_all_in_equity(
    board: List[str],
    hands: List[List[str]],
    deck: Optional[List[str]] = None,
    n: int = 100,
) -> Dict[int, float]:
    """
    :param board: (List[str])
    :param hands: (List[List[str]])
    :param hand_strength_function: (Callable)
    :param n: (int) how many sims
    :return: (Dict[int, float])
    """
    return simulate_all_in_equity(
        board=board,
        hands=hands,
        hand_strength_function=get_best_hands_fast,
        deck=deck,
        n=n,
    )


def get_best_hands_fast(board, hands):
    """get the index of the best holdem hand given a board

    :param board: ([str]) list of 5 cards
    :param hands: ([set(str)]) list of sets of 4 cards
    :return: ([[int]]) indices of `hands` that makes the strongest holdem hand
        --> this is a list of lists because it is possible to "chop" with
            every hand rank except straight flushes, quads and flushes
    """
    return get_best_hands_generic(
        hand_strength_function=get_hand_strength_fast, board=board, hands=hands
    )


def get_hand_strength_fast(board, hand) -> Tuple:
    """
    :param board: (set(str)) set of 5 cards
    :param hand: (set(str)) set of 4 cards
    :return: (tuple)
    """
    _validate_board(board)
    _validate_hand(hand)
    # TODO: not this!
    return brute_force_holdem_rank(board, hand)


def _validate_board(board):
    """raise exception if board doesn't have exactly 5 cards
    :param board: (set(str)) set of 5 cards
    :return:
    """
    if len(board) != 5:
        raise ValueError(
            f"holdem.utils.get_best_hand: "
            f"board must have 5 cards\n"
            f"input: {board}"
        )


def _validate_hand(hand):
    """raise exception if all hands don't have exactly 4 cards

    :param hand: (set(str)) set of 4 cards
    :return: None
    """
    if len(hand) != 2:
        raise ValueError(
            f"holdem.utils._validate_hands: "
            f"all hands must have 2 cards\n"
            f"invalid hand: {hand}"
        )
