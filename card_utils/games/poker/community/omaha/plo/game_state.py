from card_utils.games.poker.community.omaha.game_state import OmahaGameState


class PLOGameState(OmahaGameState):
    """ class for PLO game state """

    name = 'PLO'

    @property
    def max_bet(self):
        """ in PLO, the most you can bet is the pot,
            and the most you can raise is 2x the bet + the pot

        :return: (int)
        """
        return 2 * self.amount_to_call + self.pot.total_money
