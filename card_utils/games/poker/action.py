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

    zeros = {action_fold, action_check, action_draw}
    aggressions = {action_bet, action_raise}
    closes = {action_fold, action_call}
    passes = {action_check, action_fold}
    wagers = {action_call, *aggressions}
    actions = {*zeros, *wagers}

    def __init__(self, player, street, action, amount=0):
        """
        :param player: (int) player in game, 0-indexed
        :param street: (int) 1-indexed
        :param action: (str) one of self.valid_action_types
        :param amount: (int) amount if any
        """
        if action not in self.actions:
            raise TypeError(
                f'StreetAction: Invalid action_type {action} '
                f'on street {street}'
            )

        if amount < 0:
            raise ValueError(
                f'StreetAction: amount must be >= 0, received {amount}'
            )

        if action in self.zeros:
            if amount != 0:
                raise ValueError(
                    f'StreetAction: amount must be 0 '
                    f'for actions of type {action}'
                )
        elif action in self.wagers:
            if amount <= 0:
                raise ValueError(
                    f'StreetAction: amount must be > 0 '
                    f'for actions of type {action}'
                )

        self.player = player
        self.street = street
        self.action = action
        self.amount = amount