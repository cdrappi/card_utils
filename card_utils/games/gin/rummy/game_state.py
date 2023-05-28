from typing import List, Optional
from card_utils.deck.utils import Card
from card_utils.games.gin.game_state import AbstractGinGameState
from card_utils.games.gin.rummy.utils import split_melds
from card_utils.games.gin.utils import RummyTurn

GIN_RUMMY_MAX_SHUFFLES = 0
GIN_RUMMY_CARDS_DEALT = 10
GIN_RUMMY_END_CARDS_IN_DECK = 2


class GinRummyGameState(AbstractGinGameState):
    def __init__(
        self,
        deck: List[str],
        discard: List[str],
        p1_hand: List[str],
        p2_hand: List[str],
        turn: RummyTurn,
        public_hud=None,
        last_draw=None,
        last_draw_from_discard=None,
        is_complete=False,
        turns: int = 0,
        p1_points: Optional[int] = None,
        p2_points: Optional[int] = None,
        max_turns: Optional[int] = None,
    ) -> None:
        super().__init__(
            deck=deck,
            discard=discard,
            p1_hand=p1_hand,
            p2_hand=p2_hand,
            turn=turn,
            public_hud=public_hud,
            last_draw=last_draw,
            last_draw_from_discard=last_draw_from_discard,
            is_complete=is_complete,
            turns=turns,
            p1_points=p1_points,
            p2_points=p2_points,
            max_turns=max_turns,
            cards_dealt=GIN_RUMMY_CARDS_DEALT,
            shuffles=0,
            max_shuffles=GIN_RUMMY_MAX_SHUFFLES,
            end_cards_in_deck=GIN_RUMMY_END_CARDS_IN_DECK,
        )

    @staticmethod
    def get_deadwood(hand: List[str], melds: Optional[List[List[Card]]] = None) -> int:
        _, _, deadwood = split_melds(hand, melds)
        return deadwood

    @staticmethod
    def sort_hand(hand: List[str]) -> List[str]:
        best_melds, unmelded, _ = split_melds(hand)
        return [c for m in best_melds for c in m] + unmelded

    @staticmethod
    def advance_turn(turn: RummyTurn, deadwood: int) -> RummyTurn:
        """set next player to draw

        :return: None
        """
        if turn == RummyTurn.P1_DRAWS:
            return RummyTurn.P1_DISCARDS
        elif turn == RummyTurn.P1_DISCARDS:
            if deadwood <= 10:
                return RummyTurn.P1_MAY_KNOCK
            else:
                return RummyTurn.P2_DRAWS
        elif turn == RummyTurn.P1_MAY_KNOCK:
            return RummyTurn.P2_DRAWS

        elif turn == RummyTurn.P2_DRAWS:
            return RummyTurn.P2_DISCARDS
        elif turn == RummyTurn.P2_DISCARDS:
            if deadwood <= 10:
                return RummyTurn.P2_MAY_KNOCK
            else:
                return RummyTurn.P1_DRAWS
        elif turn == RummyTurn.P2_MAY_KNOCK:
            return RummyTurn.P1_DRAWS

        raise ValueError(f"Invalid Gin Rummy turn: {turn}")
