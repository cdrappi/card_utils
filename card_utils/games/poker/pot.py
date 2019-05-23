import collections

from card_utils.util import inverse_cumulative_sum


class Pot:
    """ class to handle side-pot logic """

    def __init__(self, num_players):
        """
        :param num_players: (int)
        """
        self.num_players = num_players
        self.money_from = collections.Counter()

    def put_money_in(self, player, amount):
        """
        :param player: (int) index
        :param amount: (int) chips
        """
        self.money_from[player] += amount

    def settle_showdown(self, winning_players):
        """
        :param winning_players: ([[int]]) list of player indexes
            who made it to showdown,
            sorted by strength of their hand,
            with the strongest hand first
        :return: ({int: int}) player index --> amount won
        """
        payouts = {p: 0 for p in range(self.num_players)}

        for winner_tier in winning_players:
            incremental_amounts = self.get_incremental_amounts(winner_tier)
            for amount in incremental_amounts:
                players = [w for w in winner_tier if self.money_from[w] >= amount]
                money_from_p = {
                    p: min(self.money_from[p], amount) / len(players)
                    for p in range(self.num_players)
                }
                for w in players:
                    for p in range(self.num_players):
                        from_p = money_from_p[p]
                        self.money_from[p] -= from_p
                        payouts[w] += from_p
                        print(f'{amount}: {w} wins {from_p} from {p} chopping {len(players)} ways')

            if self.total_money == 0:
                # we can terminate when there's no money left
                return payouts

        raise Exception(
            f'Reached end of loop in Pot.settle_showdown, '
            f'but there is still {self.total_money} '
            f'in the pot!'
        )

    @property
    def total_money(self):
        """ sum of all the money in the pot from each player

        :return: (int)
        """
        return sum(self.money_from.values())

    def get_incremental_amounts(self, players):
        """
        :param players: ([int])
        :return: ([int])
        """
        cumulative_amounts = sorted(self.money_from[p] for p in players)
        return inverse_cumulative_sum(cumulative_amounts)
