import unittest

from card_utils.games.poker.community.omaha.hutchinson import hi_point_count


class BestOmahaHighHandTestCase(unittest.TestCase):
    """ Test for the Omaha hi hutchinson point count

        cases come directly from:
            http://erh.homestead.com/omaha.html
    """

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
            hand=['As', 'Ks', 'Ah', 'Kh'],
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
            hand=['9s', '8s', '9d', '8d'],
            expected_value=32
        )

    def test_queen_nine_rainbow(self):
        """
        With the QS, QD,9H, and 9C,
        no points are earned under step one
        as there are no suited cards.
        Step two gives 14 points for the pair of queens
        and 10 points for the pair of eights. [sic]
        Step three awards 8 points for the Q-9 combination
        but then calls for a deduction of 4 points
        because of the two card gap that exists
        between the two cards.
        The final total is 28 points
        """
        self._test_hi_point_count(
            hand=['Qs', 'Qd', '9h', '9c'],
            expected_value=28
        )

    def test_single_suited_broadway(self):
        """
        An example of a hand that tends to be somewhat over-rated
        by novice players is AS, KD, QH, and TS.
        Under step one the hand receives 8 points
        for the suited ace and ten.
        Step two is disregarded as the hand does not contain any pairs.
        Step three awards 23 points for the straight potential
        of the four connected cards.
        The final total is only 31 points
        """
        self._test_hi_point_count(
            hand=['As', 'Kd', 'Qh', 'Ts'],
            # NOTE: Hutchinson actually gets this incorrect,
            #       as step three should only award the hand 19 points,
            #       because it has an ace!
            expected_value=27
        )

    def test_wheel_broadway_double_suited(self):
        """
        Finally, consider AS, 3S, KD, 4D.
        Step one awards 14 points, step two awards none,
        and step three grants 12 points for the A-3-4 combination
        and 4 points for the A-K combination.
        This total of 30 points
        """
        self._test_hi_point_count(
            hand=['As', '3s', 'Kd', '4d'],
            expected_value=30
        )
