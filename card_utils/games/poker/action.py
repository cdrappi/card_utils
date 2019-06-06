""" validate poker actions with class """


class Action:
    """ represent an action on a given street """

    # when the action is open or checked to you
    action_check = 'CHECK'
    action_bet = 'BET'

    # when there is a bet to you
    action_fold = 'FOLD'
    action_call = 'CALL'
    action_raise = 'RAISE'

    # for drawing games
    action_draw = 'DRAW'

    zero_to_call = {action_bet, action_check, action_draw}
    nonzero_to_call = {action_fold, action_call, action_raise}

    zeros = {action_fold, action_check, action_draw}
    aggressions = {action_bet, action_raise}
    closes = {action_fold, action_call}
    passes = {action_check, action_fold}
    wagers = {action_call, *aggressions}
    actions = {*zeros, *wagers}

    def __init__(self, player, action, amount):
        """
        :param player: (int) player in game, 0-indexed
        :param action: (str) one of self.valid_action_types
        :param amount: (int) amount, 0 for CHECK/FOLD/DRAW
        """
        if action not in self.actions:
            raise TypeError(f'Action: Invalid action {action}')

        if amount < 0:
            raise ValueError(
                f'Action: amount must be >= 0, received {amount}'
            )

        if action in self.zeros:
            if amount != 0:
                raise ValueError(
                    f'Action: amount must be 0 '
                    f'for actions of type {action}'
                )
        elif action in self.wagers:
            if amount <= 0:
                raise ValueError(
                    f'Action: amount must be > 0 '
                    f'for actions of type {action}'
                )

        self.player = player
        self.action = action
        self.amount = amount

    def to_dict(self):
        """
        :return: (dict)
        """
        return {
            'player': self.player,
            'action': self.action,
            'amount': self.amount
        }
