from card_utils.games.poker.action import Action
from card_utils.games.poker.community.omaha.game_state import OmahaGameState


class PLOGameState(OmahaGameState):
    """ class for PLO game state """

    name = 'PLO'

    def build_action(self, player, action, amount):
        action_obj = super().build_action(player, action, amount)
        if action_obj.action in Action.aggressions:
            if action_obj.amount > self.max_bet:
                raise ValueError(
                    f'Invalid {action_obj.action} size: '
                    f'amount {action_obj.amount} '
                    f'is greater than the pot-limit of {self.max_bet}'
                )

    @property
    def max_bet(self):
        """ in PLO, the most you can bet is the pot,
            and the most you can raise is 2x the bet + the pot

        :return: (int)
        """
        return 2 * self.amount_to_call + self.pot.total_money
