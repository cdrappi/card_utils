import unittest

from card_utils.games.poker.pot import Pot


class PotTestCase(unittest.TestCase):
    """ Test for logic in Pot class """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _dry_test(self, n, amounts_in, winning_players, expected_payouts):
        """
        :param n: (int)
        :param amounts_in: ({int: int})
        :param winning_players: ([[int]])
        :param expected_payouts: ({int: int})
        :return:
        """
        self.assertEqual(n, len(amounts_in))
        self.assertEqual(n, sum(1 for wt in winning_players for _ in wt))

        # for brevity, allow input of this function to exclude
        # players who are expected to receive 0 in payout
        for p in range(n):
            if p not in expected_payouts:
                expected_payouts[p] = 0

        pot = Pot(n)
        for p, amt_in in amounts_in.items():
            pot.put_money_in(p, amt_in)

        payouts = pot.settle_showdown(winning_players)
        self.assertEqual(payouts, expected_payouts)

    def test_heads_up_winner(self):
        """ heads up, 1 player wins it all """
        self._dry_test(
            n=2,
            amounts_in={0: 10, 1: 10},
            winning_players=[[1], [0]],
            expected_payouts={1: 20}
        )

    def test_heads_up_uneven_entered(self):
        """ heads up, 1 player puts in more money than the other """
        self._dry_test(
            n=2,
            amounts_in={0: 20, 1: 10},
            winning_players=[[1], [0]],
            expected_payouts={0: 10, 1: 20}
        )

    def test_heads_up_chopped_pot(self):
        """ test a chopped pot with uneven amounts in and out """
        self._dry_test(
            n=2,
            amounts_in={0: 20, 1: 10},
            winning_players=[[0, 1]],
            expected_payouts={0: 20, 1: 10}
        )
