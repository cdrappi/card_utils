import json
import time
import unittest

from card_utils.games.poker import (
    hand_order,
    inverse_hand_order,
    STRAIGHT_FLUSH,
    FULL_HOUSE,
    STRAIGHT,
    ONE_PAIR,
)
from card_utils.games.poker.community.omaha.brute_force import (
    get_best_hands_brute_force,
    brute_force_omaha_hi_rank,
)
from card_utils.games.poker.community.omaha.utils import (
    get_hand_strength_fast,
    get_best_hands_fast,
    get_best_straight,
    get_possible_straights,
)
from card_utils.games.poker.five_card_hand_rank import five_card_hand_rank
from card_utils.games.poker.util import pretty_hand_rank
from card_utils.util import untuple_dict
from tests.games.poker.util import deal_random_board_hands


class BestOmahaHighHandTestCase(unittest.TestCase):
    """ Test for the best Omaha high hand """

    n_random_cases = 100
    n_cases_speed_test = 100

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # @unittest.skip("uncomment if we don't want to test speeds!")
    def test_speeds(self):
        speed_test_cases = [
            deal_random_board_hands(n_hands=8, n_cards=4)
            for _ in range(self.n_cases_speed_test)
        ]
        start_brute_force = time.time()
        brute_force_results = [
            get_best_hands_brute_force(board, hands)
            for board, hands in speed_test_cases
        ]
        brute_force_time = time.time() - start_brute_force

        start_calc = time.time()
        calc_results = [
            get_best_hands_fast(board, hands)
            for board, hands in speed_test_cases
        ]
        calc_time = time.time() - start_calc

        self.assertEqual(brute_force_results, calc_results)
        self.assertGreater(brute_force_time, calc_time)
        print(
            f'\nbrute force time: {brute_force_time:.2f}'
            f'\ncalc time: {calc_time:.2f}'
            f'\n'
        )

    # @unittest.skip("uncomment me if we don't want to test random cases")
    def test_random_cases(self):
        for _ in range(self.n_random_cases):
            board, hands = deal_random_board_hands(n_hands=8, n_cards=4)
            self._assert_best_hands(board, hands)
            for hand in hands:
                self._assert_equal_hands(board, hand)

    def _assert_best_hands(self, board, hands):
        """
        :param board: ([str])
        :param hands: ([{str}]) list of set of cards
        """
        brute_force_hand_order = get_best_hands_brute_force(board, hands)
        fast_hand_order = get_best_hands_fast(board, hands)

        self.assertEqual(brute_force_hand_order, fast_hand_order)

    def _assert_both_hand_orders(self, board, hand, correct_order):
        """
        :param board: ([str])
        :param hand: ([str])
        :param correct_order: (int)
        """
        bf_order, *true_kickers = brute_force_omaha_hi_rank(board, hand)
        calc_order, *calc_kickers = get_hand_strength_fast(board, hand)

        bf_pretty_rank = pretty_hand_rank((bf_order, *true_kickers))
        calc_pretty_rank = pretty_hand_rank((calc_order, *calc_kickers))

        self._assert_equal_orders(
            board=board,
            hand=hand,
            correct_order=correct_order,
            test_order=bf_order,
            test_name='brute force'
        )
        self._assert_equal_orders(
            board=board,
            hand=hand,
            correct_order=correct_order,
            test_order=calc_order,
            test_name='calculated'
        )

        self.assertEqual(
            first=bf_order,
            second=calc_order,
            msg=(
                f'Unequal hand ranks for {hand} on {board}:\n'
                f'Brute force: {bf_pretty_rank}\n'
                f'Calculated: {calc_pretty_rank}'
            )
        )

    def _assert_equal_hands(self, board, hand):
        """
        :param board: ([str])
        :param hand: ([str])
        """
        bf_order, *bf_kickers = brute_force_omaha_hi_rank(board, hand)
        calc_order, *calc_kickers = get_hand_strength_fast(board, hand)
        self._assert_equal_orders(
            board=board,
            hand=hand,
            correct_order=bf_order,
            test_order=calc_order,
            test_name='calc vs. brute force'
        )

        self.assertEqual(
            first=bf_kickers,
            second=calc_kickers,
            msg=(
                f'\n'
                f'Incorrect kickers for {inverse_hand_order[bf_order]} '
                f'{hand}\n'
                f'on board {board}:\n'
                f'BF kickers:   {bf_kickers}\n'
                f'Calc kickers: {calc_kickers}'
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
                f'Expected {inverse_hand_order[correct_order]}, '
                f'received {inverse_hand_order[test_order]}')
        )

    def _assert_correct_straight(self, board, hand, exp_poss_straights, expected_high_card):
        board_ranks = [r for r, _ in board]
        poss_straights = get_possible_straights(board_ranks)

        tested_not_correct = set(poss_straights) - set(exp_poss_straights)
        correct_not_tested = set(exp_poss_straights) - set(poss_straights)

        incorrect_items = {
            hole_cards: highest_value
            for hole_cards, highest_value in poss_straights
            if hole_cards in tested_not_correct
        }
        missing_items = {
            hole_cards: highest_value for
            hole_cards, highest_value in exp_poss_straights
            if hole_cards in correct_not_tested
        }

        self.assertFalse(
            expr=tested_not_correct,
            msg=(
                f'Board: {board}\n'
                f'Incorrect items in tested possible straights:\n'
                f'{incorrect_items}\n'
            )
        )
        self.assertFalse(
            expr=correct_not_tested,
            msg=(
                f'Board: {board}\n'
                f'Missing items in tested possible straights:\n'
                f'{missing_items}\n'
            )
        )

        self.assertEqual(
            first=poss_straights,
            second=exp_poss_straights,
            msg=(
                f'Incorrect possible straights on board {board}'
                f'\n'
                f'Correct: '
                f'\n'
                f'{json.dumps(untuple_dict(exp_poss_straights), indent=4)}'
                f'\n'
                f'Tested: '
                f'\n'
                f'{json.dumps(untuple_dict(poss_straights), indent=4)}'
            )
        )
        best_straight = get_best_straight(poss_straights, hand)
        self.assertEqual(best_straight, expected_high_card)
        self._assert_both_hand_orders(board, hand, hand_order[STRAIGHT])

    def test_boat_with_quads_on_board(self):
        board = ['Qc', 'Qs', 'Qd', 'Qh', 'Kc']
        hand = ['As', 'Jd', 'Jc', '5h']
        self._assert_both_hand_orders(board, hand, hand_order[FULL_HOUSE])

    def test_pocket_pair(self):
        board = ['3c', 'Qh', 'Kd', '2s', '7h']
        hand = ['Ah', 'Td', '9c', 'Ac']
        self._assert_both_hand_orders(board, hand, hand_order[ONE_PAIR])

    def test_two_boats(self):
        board = ['3d', '2c', '8s', '3h', '3c']
        hand = ['5s', '2h', '8h', '8c']
        test_order, *test_kickers = brute_force_omaha_hi_rank(board, hand)
        calc_order, *calc_kickers = get_hand_strength_fast(board, hand)

        self._assert_both_hand_orders(board, hand, hand_order[FULL_HOUSE])
        self.assertEqual(
            first=test_kickers,
            second=calc_kickers,
            msg=(
                f'\n'
                f'Board: {board}'
                f'\n'
                f'Hand: {hand}'
                f'\n'
                f'Brute force says '
                f'{test_kickers[0]} full of {test_kickers[1]}'
                f'\n'
                f'Speed calc says '
                f'{calc_kickers[0]} full of {calc_kickers[1]}'
            )
        )

    def test_boat_with_trips_in_hand(self):
        board = ['Ad', 'Jc', '4s', '4c', '4d']
        hand = ['7h', 'Ts', '7c', '7d']
        calc_order, *calc_kickers = get_hand_strength_fast(board, hand)

        self._assert_both_hand_orders(board, hand, hand_order[FULL_HOUSE])
        self.assertEqual(
            first=calc_kickers,
            second=[4, 7],
            msg=(
                f'Incorrect full house calculation\n'
                f'Expected 4 full of 7, ',
                f'received {calc_kickers[0]} full of {calc_kickers[1]}'
            )
        )

    def test_multiple_possible_straights(self):
        board = ['Ah', '7s', '3h', '4c', '5s']
        hand = ['Tc', 'Qh', '4d', '6s']
        expected_possible_straights = {
            (1, 2): 5,
            (2, 3): 5,
            (2, 4): 5,
            (2, 5): 5,
            (2, 6): 6,
            (3, 6): 7,
            (4, 6): 7,
            (5, 6): 7,
            (6, 7): 7,
            (6, 8): 8
        }
        self._assert_correct_straight(board, hand, expected_possible_straights, 7)

    def test_nut_flush_over_second_nut_flush(self):
        board = ['2h', 'Qs', '9d', '5s', '3s']
        hands = [
            ['7d', 'Ts', 'Tc', 'Ks'],
            ['7s', '4d', 'As', 'Jh']
        ]

        for hand in hands:
            self._assert_equal_hands(board, hand)

        self._assert_best_hands(board, hands)

    def test_steel_wheel(self):
        board = ['5h', 'Ah', 'Tc', '3h', 'Ts']
        hand = ['7d', '8s', '2h', '4h']

        self._assert_both_hand_orders(board, hand, hand_order[STRAIGHT_FLUSH])

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

    def test_broadway(self):
        board = ['As', '2d', 'Jc', 'Tc', 'Jh']
        hand = ['9h', 'Kh', '2s', 'Qh']
        expected_possible_straights = {
            (12, 13): 14,
        }
        self._assert_correct_straight(board, hand, expected_possible_straights, 14)

    def test_many_straight_cards_straight(self):
        board = ['Ts', '7d', '4h', '2c', '5h']
        hand = ['8h', '9c', '8c', '6h']
        expected_possible_straights = {
            (6, 8): 8,
            (3, 6): 7,
            (1, 3): 5,
        }
        self._assert_correct_straight(board, hand, expected_possible_straights, 8)

    def test_brute_force_full_house(self):
        hand_order_, *cards = five_card_hand_rank(
            five_card_hand=['2c', 'Ac', 'Ad', '2d', 'As']
        )
        self.assertEqual(hand_order_, hand_order[FULL_HOUSE])

    def test_straight_over_trips(self):
        board = ['Ts', '7d', '4h', '2c', '5h']
        hands = [
            ['8h', '9c', '8c', '6h'],
            ['6c', '4c', '4d', 'Qh']
        ]
        self._assert_best_hands(board, hands)

    def test_two_pair_on_paired_board(self):
        board = ['Kh', 'Qc', 'Ks', 'Qh', '6h']
        hand = ['4c', '5d', '8d', '4d']
        self._assert_equal_hands(board, hand)

    def test_three_of_a_kind_on_quads_board(self):
        board = ['Qh', 'Qs', 'Qc', 'Qd', '8d']
        hand = ['2h', 'Ts', 'Jd', '4d']
        self._assert_equal_hands(board, hand)

    def test_boat_with_trips_in_hand(self):
        board = ['3d', 'Qh', '3s', 'Ts', '3c']
        hand = ['Th', 'Qs', 'Qc', 'Qd']
        self._assert_equal_hands(board, hand)
