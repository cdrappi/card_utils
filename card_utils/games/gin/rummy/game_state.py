

class GinRummyGameState:

    def __init__(self,
                 deck, discard,
                 p1_hand, p2_hand,
                 p1_discards, p1_draws, p2_discards, p2_draws,
                 public_hud=None, last_draw=None, last_draw_from_discard=None,
                 is_complete=False, turns=0, shuffles=0,
                 p1_points=None, p2_points=None,
                 max_shuffles=None, max_turns=None,
                 ) -> None:
        pass