import unittest

from card_utils.games.poker.pot import Pot


class PotTestCase(unittest.TestCase):
    """ Test for logic in Pot class """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _dry_test(self,
                  amounts_in,
                  winning_players,
                  rake_fraction,
                  max_rake,
                  expected_payouts,
                  expected_rakes):
        """
        :param amounts_in: ({int: int})
        :param winning_players: ([[int]])
        :param expected_payouts: ({int: int})
        :return:
        """
        n = len(amounts_in)

        # for brevity, allow input of this function to exclude
        # players who are expected to receive 0 in payout
        for p in range(n):
            if p not in expected_payouts:
                expected_payouts[p] = 0

        pot = Pot(n, rake_fraction, max_rake)
        for p, amt_in in amounts_in.items():
            pot.put_money_in(p, amt_in)

        payouts, rakes = pot.settle_showdown(winning_players, rake_pot=True)
        self.assertEqual(payouts, expected_payouts)
        self.assertEqual(rakes, expected_rakes)

    def test_heads_up_winner(self):
        """ heads up, 1 player wins it all """
        self._dry_test(
            amounts_in={0: 10, 1: 10},
            winning_players=[[1], [0]],
            rake_fraction=0.0,
            max_rake=0,
            expected_payouts={1: 20},
            expected_rakes={0: 0, 1: 0}
        )

    def test_heads_up_chopped_pot(self):
        """ test a chopped pot with uneven amounts in and out """
        self._dry_test(
            amounts_in={0: 20, 1: 10},
            winning_players=[[0, 1]],
            rake_fraction=0.0,
            max_rake=0,
            expected_payouts={0: 20, 1: 10},
            expected_rakes={0: 0, 1: 0},
        )

    def test_three_way_uneven_entered(self):
        """ heads up, 1 player puts in more money than the other """
        self._dry_test(
            amounts_in={0: 20, 1: 10, 2: 0},
            winning_players=[[1], [0]],
            rake_fraction=0.0,
            max_rake=0,
            expected_payouts={0: 10, 1: 20},
            expected_rakes={0: 0, 1: 0, 2: 0},
        )

    def test_4_way_multi_balance_chop(self):
        """ test a complex 4-way chop """
        self._dry_test(
            amounts_in={0: 10, 1: 20, 2: 30, 3: 40},
            winning_players=[[1], [2, 3]],
            rake_fraction=0.0,
            max_rake=0,
            expected_payouts={
                1: 70,
                2: 10,
                3: 20,
            },
            expected_rakes={0: 0, 1: 0, 2: 0, 3: 0},
        )

    def test_eight_way_everyone_gets_stacked(self):
        """ player p has 10*p chips,
            and everyone loses to player 7, the big stack
        """
        starting_stacks = {i: 10 * i for i in range(8)}
        self._dry_test(
            amounts_in=starting_stacks,
            winning_players=[[7]],
            rake_fraction=0.0,
            max_rake=0,
            expected_payouts={7: sum(starting_stacks.values())},
            expected_rakes={i: 0 for i in starting_stacks},
        )

    def test_eight_way_multi_balance_chop(self):
        """ test a complex 8-way chop """
        starting_stacks = {i: 10 * i for i in range(8)}
        self._dry_test(
            amounts_in=starting_stacks,
            winning_players=[[4, 3], [6], [7]],
            rake_fraction=0.0,
            max_rake=0,
            expected_payouts={
                3: 90,
                4: 130,
                6: 50,
                7: 10
            },
            expected_rakes={i: 0 for i in starting_stacks},
        )
    
    def test_heads_up_winner_raked(self):
        """ heads up, 1 player wins it all """
        self._dry_test(
            amounts_in={0: 10, 1: 10},
            winning_players=[[1], [0]],
            rake_fraction=0.10,
            max_rake=5,
            expected_payouts={1: 20},
            expected_rakes={0: 0, 1: 0}
        )

    def test_heads_up_chopped_pot_raked(self):
        """ test a chopped pot with uneven amounts in and out """
        self._dry_test(
            amounts_in={0: 20, 1: 10},
            winning_players=[[0, 1]],
            rake_fraction=0.10,
            max_rake=5,
            expected_payouts={0: 18, 1: 9},
            expected_rakes={0: 2, 1: 1},
        )

    def test_three_way_uneven_entered_raked(self):
        """ heads up, 1 player puts in more money than the other """
        self._dry_test(
            amounts_in={0: 20, 1: 10, 2: 0},
            winning_players=[[1], [0]],
            rake_fraction=0.10,
            max_rake=5,
            expected_payouts={0: 10, 1: 20},
            expected_rakes={0: 0, 1: 0, 2: 0},
        )

    def test_4_way_multi_balance_chop_raked(self):
        """ test a complex 4-way chop """
        self._dry_test(
            amounts_in={0: 10, 1: 20, 2: 30, 3: 40},
            winning_players=[[1], [2, 3]],
            rake_fraction=0.10,
            max_rake=5,
            expected_payouts={
                1: 70,
                2: 10,
                3: 20,
            },
            expected_rakes={0: 0, 1: 0, 2: 0, 3: 0},
        )

    def test_eight_way_everyone_gets_stacked_raked(self):
        """ player p has 10*p chips,
            and everyone loses to player 7, the big stack
        """
        starting_stacks = {i: 10 * i for i in range(8)}
        self._dry_test(
            amounts_in=starting_stacks,
            winning_players=[[7]],
            rake_fraction=0.10,
            max_rake=5,
            expected_payouts={7: sum(starting_stacks.values())},
            expected_rakes={i: 0 for i in starting_stacks},
        )

    def test_eight_way_multi_balance_chop_raked(self):
        """ test a complex 8-way chop """
        starting_stacks = {i: 10 * i for i in range(8)}
        self._dry_test(
            amounts_in=starting_stacks,
            winning_players=[[4, 3], [6], [7]],
            rake_fraction=0.10,
            max_rake=5,
            expected_payouts={
                3: 90,
                4: 130,
                6: 50,
                7: 10
            },
            expected_rakes={i: 0 for i in starting_stacks},
        )
