import random
from typing import Callable, List

from card_utils.deck import cards


def simulate_all_in_equity(
    board: List[str],
    hands: List[List[str]],
    hand_strength_function: Callable,
    deck: List[str] = None,
    n: int = 100
) -> List[float]:
    """
    :param board: (List[str])
    :param hands: (List[List[str]])
    :param hand_strength_function: (Callable)
    :param n: (int) how many sims
    :return: (List[float])
    """
    if deck is None:
        used_cards = {*board, *{c for hand in hands for c in hand}}
        deck = set(cards) - used_cards

    cards_to_come = 5 - len(board)
    win_shares = {p: 0.0 for p, _ in enumerate(hands)}
    for _ in range(n):
        sampled_cards = random.sample(deck, cards_to_come)
        hand_strengths = hand_strength_function(
            board=board+sampled_cards,
            hands=hands
        )
        for p in hand_strengths[0]:
            win_shares[p] += 1.0 / len(hand_strengths[0]) / n
    return win_shares
