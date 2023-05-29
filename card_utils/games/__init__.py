from typing import Dict, List, Tuple

from card_utils.deck import ace_high_rank_to_value, suits
from card_utils.deck.utils import suit_partition


def canonize_hand(hand: List[str]) -> Tuple[List[str], Dict[str, str]]:
    """
    :param hand: (List[str])
    :return: (List[str])
    """
    hand_suits = suit_partition(hand)
    # order by (#-cards, suit)
    ordered_suits = sorted(hand_suits, key=lambda k: (-len(hand_suits[k]), k))
    suit_map = dict(zip(ordered_suits, suits))
    hand = [
        f"{rank}{suit_map[suit]}"
        for suit in ordered_suits
        for rank in sorted(hand_suits[suit], key=ace_high_rank_to_value.get)  # type: ignore
    ]
    return hand, suit_map
