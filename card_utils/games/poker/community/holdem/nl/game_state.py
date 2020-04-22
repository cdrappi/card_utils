from card_utils.games.poker.community.holdem.game_state import HoldemGameState


class NLHEGameState(HoldemGameState):
    """ class for PLO game state """

    name = 'NLHE'

    @property
    def max_bet(self):
        """ in NLHE, the most you can bet all in, all the time

        :return: (int)
        """
        return HoldemGameState.max_bet.fget(self)
