from typing import List, Optional, Tuple

from card_utils.deck.utils import Card
from card_utils.games.gin.game_state import AbstractGinGameState
from card_utils.games.gin.rummy.utils import (
    get_candidate_melds,
    layoff_deadwood,
    split_melds,
)
from card_utils.games.gin.utils import RummyTurn

GIN_RUMMY_MAX_SHUFFLES = 1
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
        first_turn: RummyTurn,
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
            first_turn=first_turn,
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
            underknock_bonus=20,
            gin_bonus=20,
        )

    @staticmethod
    def get_deadwood(
        hand: List[str],
        melds: Optional[List[List[Card]]] = None,
        opp_melds: Optional[List[List[Card]]] = None,
    ) -> int:
        if opp_melds is not None:
            deadwood, _, _, _ = layoff_deadwood(hand, opp_melds)
            return deadwood
        deadwood, _, _ = split_melds(hand, melds)
        return deadwood

    @staticmethod
    def sort_hand(hand: List[str]) -> List[str]:
        _, best_melds, unmelded = split_melds(hand)
        return [c for m in best_melds for c in m] + unmelded

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
            if deadwood <= 10:
                return RummyTurn.P1_MAY_KNOCK
            else:
                return RummyTurn.P2_DRAWS
        elif current == RummyTurn.P1_MAY_KNOCK:
            return RummyTurn.P2_DRAWS

        elif current == RummyTurn.P2_DRAWS:
            return RummyTurn.P2_DISCARDS
        elif current == RummyTurn.P2_DISCARDS:
            if deadwood <= 10:
                return RummyTurn.P2_MAY_KNOCK
            else:
                return RummyTurn.P1_DRAWS
        elif current == RummyTurn.P2_MAY_KNOCK:
            return RummyTurn.P1_DRAWS

        raise ValueError(f"Invalid Gin Rummy turn: {current}")

    def get_knock_candidates(self) -> List[Tuple[int, List[List[Card]]]]:
        """
        at the end of a turn, if they can knock with
        10 or fewer points, return to them all possible
        combinations of melds they can do so with
        """
        if not self.turn.is_knock():
            return []
        hand = self.p1_hand if self.turn.p1() else self.p2_hand
        candidates = get_candidate_melds(hand, max_deadwood=10)
        return [(dw, melds) for dw, melds, _ in candidates]
