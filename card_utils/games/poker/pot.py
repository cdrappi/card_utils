import collections


class Pot:
    """ class to handle side-pot logic """

    def __init__(self, num_players):
        """
        :param num_players: (int)
        """
        self.num_players = num_players
        self.money_from_player = collections.Counter()
        self.pot = 0

    def put_money_in(self, player, amount):
        """
        :param player: (int) index
        :param amount: (int) chips
        """
        self.money_from_player[player] += amount
        self.pot += amount

    def settle_showdown(self, winners):
        """
        :param winners: ([int]) list of player indexes
            who made it to showdown,
            sorted by strength of their hand,
            with the strongest hand first
        :return: ({int: int}) player index --> amount won
        """
        payouts = {p: 0 for p in range(self.num_players)}
        for winner in winners:
            max_winnings = self.money_from_player[winner]
            for p in range(self.num_players):
                # can't win more than you risked
                winnings_from_p = min(self.money_from_player[p], max_winnings)
                payouts[winner] += winnings_from_p
                self.money_from_player[p] -= winnings_from_p

            if sum(self.money_from_player.values()) == 0:
                # we can terminate early when there's no money left
                return payouts

        return payouts
