import unittest

from card_utils.games.poker import (
    hand_order,
    STRAIGHT_FLUSH,
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

    # n_random_cases = 100

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

    def _assert_equal_orders(self, board, hand,
                             correct_order, test_order,
                             test_name):
        self.assertEqual(
            first=correct_order,
            second=test_order,
            msg=(
                f'Error in {test_name} hand order: \n'
                f'For hand {hand}\n'
                f'on board {board}\n'
                f'Expected {hand_order[correct_order]}, '
                f'received {hand_order[test_order]}')
        )

    def _test_both_hand_orders(self, board, hand, correct_order):
        bf_order, *true_kickers = brute_force_omaha_hi_rank(board, hand)
        calc_order, *calc_kickers = get_hand_strength(board, hand)

        bf_pretty_rank = pretty_hand_rank((bf_order, *true_kickers))
        calc_pretty_rank = pretty_hand_rank((calc_order, *calc_kickers))

        self._assert_equal_orders(board, hand, correct_order, bf_order, 'brute force')
        self._assert_equal_orders(board, hand, correct_order, calc_order, 'calculated')

        self.assertEqual(
            first=bf_order,
            second=calc_order,
            msg=(
                f'Unequal hand ranks for {hand} on {board}:\n'
                f'Brute force: {bf_pretty_rank}\n'
                f'Calculated: {calc_pretty_rank}'
            )
        )

    def test_nut_flush_over_second_nut_flush(self):
        board = ['2h', 'Qs', '9d', '5s', '3s']
        hands = [
            ['7d', 'Ts', 'Tc', 'Ks'],
            ['7s', '4d', 'As', 'Jh']
        ]
        self._test_best_hand(board, hands)

    def test_steel_wheel(self):
        board = ['5h', 'Ah', 'Tc', '3h', 'Ts']
        hand = ['7d', '8s', '2h', '4h']

        self._test_both_hand_orders(board, hand, hand_order[STRAIGHT_FLUSH])

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

    def test_brute_force_full_house(self):
        hand_order_, *cards = five_card_hand_rank(['2c', 'Ac', 'Ad'] + ['2d', 'As'])
        self.assertEqual(hand_order_, hand_order[FULL_HOUSE])

    def test_straight_over_trips(self):
        board = ['Ts', '7d', '4h', '2c', '5h']
        hands = [
            ['8h', '9c', '8c', '6h'],
            ['6c', '4c', '4d', 'Qh']
        ]
        self._test_best_hand(board, hands)
