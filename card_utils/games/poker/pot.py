import collections


class Pot:
    """ class to handle side-pot logic """

    def __init__(self, num_players):
        """
        :param num_players: (int)
        """
        self.num_players = num_players
        self.money_from = collections.Counter()
        self.pot = 0

    def put_money_in(self, player, amount):
        """
        :param player: (int) index
        :param amount: (int) chips
        """
        self.money_from[player] += amount
        self.pot += amount

    def settle_showdown(self, winning_players):
        """
        :param winning_players: ([[int]]) list of player indexes
            who made it to showdown,
            sorted by strength of their hand,
            with the strongest hand first
        :return: ({int: int}) player index --> amount won
        """
        # TODO: test!
        payouts = {p: 0 for p in range(self.num_players)}
        for winners in winning_players:
            n_chop = len(winners)
            for winner in winners:
                amount_in = self.money_from[winner]
                for p in range(self.num_players):
                    # can't win more than you risked
                    from_p = min(self.money_from[p], amount_in) / n_chop
                    payouts[winner] += from_p
                    self.money_from[p] -= from_p

            if sum(self.money_from.values()) == 0:
                # we can terminate early when there's no money left
                return payouts

        return payouts
