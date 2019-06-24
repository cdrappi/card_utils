from typing import List
from card_utils.util import inverse_cumulative_sum


class Pot:
    """ class to handle side-pot logic """

    def __init__(self, num_players, balances=None):
        """
        :param num_players: (int)
        :param balances: ({str: int})
        """
        self.num_players = num_players
        self.balances = balances or {p: 0 for p in range(num_players)}

    def put_money_in(self, player, amount):
        """
        :param player: (int) index
        :param amount: (int) chips
        """
        self.balances[player] += amount

    def settle_showdown(self, winning_players: List[List[int]]):
        """
        :param winning_players: ([[int]]) list of list of players who made it
            to showdown, sorted by hand strength (strongest first)
        :return: ({int: int}) player index --> amount won
        """
        payouts = {p: 0 for p in range(self.num_players)}

        for winner_tier in winning_players:
            # go over each tier of winners
            # they will chop their equity in each side pot equally
            incremental_amounts = self.get_incremental_amounts(winner_tier)
            for inc_amt in incremental_amounts:
                # get the players who are chopping this amount,
                # which should decrease each loop
                players_chopping = [
                    winner
                    for winner in winner_tier
                    if self.balances[winner] >= inc_amt
                ]
                # each player chops up as much as they can win from
                # the balance of all players (including themselves)
                money_per_winner = sum(
                    min(money_left, inc_amt) / len(players_chopping)
                    for money_left in self.balances.values()
                )
                for winner in players_chopping:
                    # apply payouts to everyone in this hand/amount tier
                    payouts[winner] += money_per_winner
                for p in range(self.num_players):
                    # and deduct balances from all players,
                    # who each paid out at most inc_amount
                    # to the winners in this tier
                    self.balances[p] = max(0, self.balances[p] - inc_amt)

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
        return sum(self.balances.values())

    def get_incremental_amounts(self, players):
        """
        :param players: ([int])
        :return: ([int])
        """
        cumulative_amounts = sorted(self.balances[p] for p in players)
        return inverse_cumulative_sum(cumulative_amounts)
