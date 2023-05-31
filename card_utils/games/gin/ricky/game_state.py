from typing import List, Optional, Tuple

from card_utils.deck.utils import Card
from card_utils.games.gin.game_state import AbstractGinGameState
from card_utils.games.gin.ricky.utils import hand_points, sort_hand
from card_utils.games.gin.utils import RummyAction, RummyTurn

GIN_RICKY_CARDS_DEALT = 7
GIN_RICKY_END_CARDS_IN_DECK = 0
GIN_RICKY_MAX_SHUFFLES = None


class GinRickyGameState(AbstractGinGameState):
    def __init__(
        self,
        deck,
        discard,
        p1_hand,
        p2_hand,
        turn: RummyTurn,
        first_turn: RummyTurn,
        public_hud=None,
        last_draw=None,
        last_draw_from_discard=None,
        is_complete=False,
        turns=0,
        p1_points=None,
        p2_points=None,
        max_turns=None,
    ) -> None:
        super().__init__(
            deck=deck,
            discard=discard,
            p1_hand=p1_hand,
            p2_hand=p2_hand,
            turn=turn,
            first_turn=first_turn,
            public_hud=public_hud,
            last_draw=last_draw,
            last_draw_from_discard=last_draw_from_discard,
            is_complete=is_complete,
            turns=turns,
            p1_points=p1_points,
            p2_points=p2_points,
            max_turns=max_turns,
            shuffles=0,
            cards_dealt=GIN_RICKY_CARDS_DEALT,
            max_shuffles=GIN_RICKY_MAX_SHUFFLES,
            end_cards_in_deck=GIN_RICKY_END_CARDS_IN_DECK,
        )

    @staticmethod
    def get_deadwood(
        hand: List[str],
        melds: Optional[List[List[Card]]] = None,
        opp_melds: Optional[List[List[Card]]] = None,
    ) -> int:
        return hand_points(hand)

    @staticmethod
    def sort_hand(hand: List[str]) -> List[str]:
        return sort_hand(hand)

    @staticmethod
    def advance_turn(
        current: RummyTurn,
        from_discard: bool,
        first_turn: RummyTurn,
        deadwood: int,
    ) -> RummyTurn:
        """set next player to draw

        :return: None
        """
        if current == RummyTurn.P1_DRAWS_FIRST:
            if from_discard:
                # they picked up a card, so they discard now
                return RummyTurn.P1_DISCARDS
            elif first_turn == RummyTurn.P2_DRAWS_FIRST:
                # they didn't pick up a card, so the other player draws
                return RummyTurn.P2_DRAWS_FROM_DECK
            else:
                return RummyTurn.P2_DRAWS_FIRST
        elif current == RummyTurn.P2_DRAWS_FIRST:
            if from_discard:
                return RummyTurn.P2_DISCARDS
            elif first_turn == RummyTurn.P1_DRAWS_FIRST:
                return RummyTurn.P1_DRAWS_FROM_DECK
            else:
                return RummyTurn.P1_DRAWS_FIRST
        elif current == RummyTurn.P1_DRAWS_FROM_DECK:
            return RummyTurn.P1_DISCARDS
        elif current == RummyTurn.P2_DRAWS_FROM_DECK:
            return RummyTurn.P2_DISCARDS
        elif current == RummyTurn.P1_DRAWS:
            return RummyTurn.P1_DISCARDS
        elif current == RummyTurn.P1_DISCARDS:
            return RummyTurn.P2_DRAWS
        elif current == RummyTurn.P2_DRAWS:
            return RummyTurn.P2_DISCARDS
        elif current == RummyTurn.P2_DISCARDS:
            return RummyTurn.P1_DRAWS

        raise ValueError(f"Invalid Gin Ricky turn: {current}")
