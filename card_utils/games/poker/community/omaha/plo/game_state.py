from card_utils.games.poker.action import Action
from card_utils.games.poker.community.omaha.game_state import OmahaGameState


class PLOGameState(OmahaGameState):
    """ class for PLO game state """

    name = 'PLO'

    def validate_action(self, action):
        """
        :param action: (Action)
        """
        super().validate_action(action)
        if action.action in Action.aggressions:
            if action.amount > self.max_bet:
                raise ValueError(
                    f'Invalid {action.action} size: '
                    f'amount {action.amount} '
                    f'is greater than the pot-limit of {self.max_bet}'
                )

    @property
    def max_bet(self):
        """ in PLO, the most you can bet is the pot,
            and the most you can raise is 2x the bet + the pot

        :return: (int)
        """
        return 2 * self.amount_to_call + self.pot.total_money
