import unittest

from card_utils.games.poker.community.omaha.hutchinson import hi_point_count


class BestOmahaHighHandTestCase(unittest.TestCase):
    """ Test for the Omaha hi hutchinson point count """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _test_hi_point_count(self, hand, expected_value):
        """
        :param hand: ([str])
        :param expected_value: (int)
        :return:
        """
        self.assertEqual(
            first=hi_point_count(hand),
            second=expected_value,
        )

    def test_ace_king_double_suited(self):
        """
        A hand containing the AS, KS, AH, and KH
        would earn 54 points under this system
        """
        self._test_hi_point_count(
            hand=['As', 'Ac', 'Ks', 'Kc'],
            expected_value=54,
        )

    def test_eight_nine_double_suited(self):
        """
        Assume you have the 9S, 8S, 9D, and 8D.
        Step one awards a total of 6 points
        for the two double suits headed by nines.
        Under step two, the pair of nines earns 10 points
        and the pair of eights earns 8 points.
        The last step awards 8 points for the 9-8 combination.
        The total of 32 points
        """
        self._test_hi_point_count(
            hand=['9s', '9c', '8s', '8c'],
            expected_value=32
        )
