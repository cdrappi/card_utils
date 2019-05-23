import unittest

from card_utils.games.poker.pot import Pot


class PotTestCase(unittest.TestCase):
    """ Test for logic in Pot class """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_heads_up_winner(self):
        """ heads up, 1 player wins it all """
        pot = Pot(2)
        pot.put_money_in(0, 10)
        pot.put_money_in(1, 10)

        winning_players = [[1], [0]]
        payouts = pot.settle_showdown(winning_players)

        expected_payouts = {
            1: 20,
            0: 0
        }
        self.assertEqual(payouts, expected_payouts)
