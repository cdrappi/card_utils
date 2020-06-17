from typing import List, Dict, Tuple
from card_utils.util import inverse_cumulative_sum


class Pot:
    """ class to handle side-pot logic """

    def __init__(self,
                 num_players: int,
                 percent_rake: float,
                 max_rake: int,
                 balances: Dict[int, int] = None):
        """
        :param num_players: (int)
        :param balances: ({int: int})
        """
        self.num_players = num_players
        self.balances = balances or {p: 0 for p in range(num_players)}
        self.percent_rake = percent_rake
        self.max_rake = max_rake
    
    def put_money_in(self, player, amount):
        """
        :param player: (int) index
        :param amount: (int) chips
        """
        self.balances[player] += amount

    def settle_showdown(self,
                        winning_players: List[List[int]],
                        rake_pot: bool
                        ) -> Tuple[Dict[int, int], Dict[int, int]]:
        """
        :param winning_players: ([[int]]) list of list of players who made it
            to showdown, sorted by hand strength (strongest first)
        :return: ({int: int}) player index --> amount won
        """
        payouts = {p: 0 for p in range(self.num_players)}
        rake_per_player = self.get_rake_per_player(rake_pot)
        for player, rake_paid in rake_per_player.items():
            self.balances[player] -= rake_paid

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
                return payouts, rake_per_player

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

    def get_max_total_rake(self):
        return min(
            self.max_rake,
            self.percent_rake / 100 * self.total_money
        )

    def get_rake_per_player(self, rake_pot: bool):
        rake_per_player = {p: 0 for p in range(self.num_players)}
        if not rake_pot:
            return rake_per_player
        max_total_rake = self.get_max_total_rake()
        balance_levels = sorted(set(self.balances.values()))
        balance_diffs = inverse_cumulative_sum(balance_levels)
        for level, diff in zip(balance_levels, balance_diffs):
            players_at_level = {
                player_id
                for player_id, b in self.balances.items()
                if b >= level
            }
            total_rake_left = max_total_rake - sum(rake_per_player.values())
            if total_rake_left == 0:
                return rake_per_player
            max_rake_at_level = int(total_rake_left / len(players_at_level))
            percent_rake_at_level = int(level * self.percent_rake / 100)
            rake_at_level = min(max_rake_at_level, percent_rake_at_level)
            for player in players_at_level:
                rake_per_player[player] += rake_at_level
                
        return rake_per_player
