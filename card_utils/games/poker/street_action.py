class StreetAction:
    """ represent an action on a given street """

    # to skip over a player who has folded
    action_pass = 'PASS'

    # when the action is open or checked to you
    action_check = 'CHECK'
    action_bet = 'BET'

    # when there is a bet to you
    action_fold = 'FOLD'
    action_call = 'CALL'
    action_raise = 'RAISE'

    # for drawing games
    action_draw = 'DRAW'

    valid_zero_amount = {
        action_pass,
        action_fold,
        action_check,
        action_draw
    }

    valid_vpip = {
        action_bet,
        action_call,
        action_raise
    }

    valid_action_types = {
        *valid_zero_amount,
        *valid_vpip,
    }

    def __init__(self, street, action_type, amount=0):
        """
        :param street: (int) 1-indexed
        :param action_type: (str)
            one of {
        """
        if action_type not in self.valid_action_types:
            raise TypeError(
                f'StreetAction: Invalid action_type {action_type} '
                f'on street {street}'
            )

        if amount < 0:
            raise ValueError(
                f'StreetAction: amount must be >= 0, received {amount}'
            )

        if action_type in self.valid_zero_amount:
            if amount != 0:
                raise ValueError(
                    f'StreetAction: amount must be 0 '
                    f'for actions of type {action_type}'
                )
        elif action_type in self.valid_vpip:
            if amount <= 0:
                raise ValueError(
                    f'StreetAction: amount must be > 0 '
                    f'for actions of type {action_type}'
                )

        self.street = street
        self.action_type = action_type
        self.amount = amount
