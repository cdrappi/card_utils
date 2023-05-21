from typing import List

from card_utils.games.gin.game_state import AbstractGinGameState


class GinRummyGameState(AbstractGinGameState):
    def __init__(
        self,
        deck,
        discard,
        p1_hand,
        p2_hand,
        p1_discards,
        p1_draws,
        p2_discards,
        p2_draws,
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
            p1_discards=p1_discards,
            p1_draws=p1_draws,
            p2_discards=p2_discards,
            p2_draws=p2_draws,
            public_hud=public_hud,
            last_draw=last_draw,
            last_draw_from_discard=last_draw_from_discard,
            is_complete=is_complete,
            turns=turns,
            p1_points=p1_points,
            p2_points=p2_points,
            max_turns=max_turns,
            shuffles=0,
            max_shuffles=1,
        )

    @staticmethod
    def get_deadwood(hand: List[str]) -> int:
        # TODO:
        return 0

    @staticmethod
    def sort_hand(hand: List[str]) -> List[str]:
        # TODO:
        return hand
