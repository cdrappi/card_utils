from typing import List

from card_utils.games.gin.game_state import AbstractGinGameState
from card_utils.games.gin.ricky.utils import hand_points, sort_hand


class GinRickyGameState(AbstractGinGameState):
    @staticmethod
    def get_deadwood(hand: List[str]) -> int:
        return hand_points(hand)

    @staticmethod
    def sort_hand(hand: List[str]) -> List[str]:
        return sort_hand(hand)
