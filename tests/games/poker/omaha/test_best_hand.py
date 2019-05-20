import unittest

from card_utils.games.poker import (
    hand_order,
    FULL_HOUSE,
)
from card_utils.games.poker.five_card_hand_rank import five_card_hand_rank
from card_utils.games.poker.omaha.brute_force import (
    get_best_hand_brute_force,
    brute_force_omaha_hi_rank,
)
from card_utils.games.poker.omaha.utils import (
    get_best_hand,
    get_hand_strength,
    get_best_straight,
    get_possible_straights,
)
from card_utils.games.poker.util import pretty_hand_rank
from tests.games.poker.util import deal_random_board_hands


class BestOmahaHighHandTestCase(unittest.TestCase):
    """ Test for the best Omaha high hand """

    n_random_cases = 0

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_random_cases(self):
        for _ in range(self.n_random_cases):
            board, hands = deal_random_board_hands(n_hands=8, n_cards=4)
            self._test_best_hand(board, hands)

    def _test_best_hand(self, board, hands):
        """
        :param board: ([str])
        :param hands: ([{str}]) list of set of cards
        """
        true_best_hand_index = get_best_hand_brute_force(board, hands)
        test_best_hand_index = get_best_hand(board, hands)

        true_hand_rank = brute_force_omaha_hi_rank(board, hands[true_best_hand_index])
        calc_hand_rank = get_hand_strength(board, hands[test_best_hand_index])

        true_pretty_rank = pretty_hand_rank(true_hand_rank)
        calc_pretty_rank = pretty_hand_rank(calc_hand_rank)

        self.assertEqual(
            first=true_best_hand_index,
            second=test_best_hand_index,
            msg=(
                f'Board: {board}\n'
                f'Best hand is {hands[true_best_hand_index]} ({true_pretty_rank})\n'
                f'Test value: {hands[test_best_hand_index]} ({calc_pretty_rank})'
            )
        )

    def test_non_straight(self):
        board = ['3h', '9d', 'Js', '2c', '4h']
        hand = ['9h', '5h', '7s', '8c']
        board_ranks = [r for r, _ in board]
        possible_straights = get_possible_straights(board_ranks)
        expected_possible_straights = {
            (1, 5): 5,
            (5, 6): 6,
        }

        self.assertEqual(
            first=possible_straights,
            second=expected_possible_straights
        )
        best_straight = get_best_straight(possible_straights, hand)
        self.assertEqual(best_straight, 0)

    @unittest.skip('passes')
    def test_straight(self):
        board = ['Ts', '7d', '4h', '2c', '5h']
        hand = ['8h', '9c', '8c', '6h']
        board_ranks = [r for r, _ in board]
        possible_straights = get_possible_straights(board_ranks)
        expected_possible_straights = {
            (6, 8): 8,
            (3, 6): 7,
            (1, 3): 5,
        }

        self.assertEqual(
            first=possible_straights,
            second=expected_possible_straights
        )
        best_straight = get_best_straight(possible_straights, hand)
        self.assertEqual(best_straight, 8)

    @unittest.skip('passes')
    def test_brute_force_full_house(self):
        board = ['2c', 'Ac', '4h', 'Ad', '3c']
        hand = ['8h', '2d', '9d', 'As']
        # hand_order_, *cards = brute_force_omaha_hi_rank(board, hand)
        hand_order_, *cards = five_card_hand_rank(['2c', 'Ac', 'Ad'] + ['2d', 'As'])
        self.assertEqual(hand_order_, hand_order[FULL_HOUSE])

    @unittest.skip('passes')
    def test_straight_over_trips(self):
        board = ['Ts', '7d', '4h', '2c', '5h']
        hands = [
            ['8h', '9c', '8c', '6h'],
            ['6c', '4c', '4d', 'Qh']
        ]
        self._test_best_hand(board, hands)
