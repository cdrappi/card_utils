import json
import unittest

from card_utils.games.poker import (
    hand_order,
    inverse_hand_order,
    STRAIGHT_FLUSH,
    FULL_HOUSE,
    STRAIGHT,
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
from card_utils.util import json_dumpable_tuple_dict
from tests.games.poker.util import deal_random_board_hands


class BestOmahaHighHandTestCase(unittest.TestCase):
    """ Test for the best Omaha high hand """

    n_random_cases = 0

    n_random_cases = 10000
    print_every_n_cases = 100

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_random_cases(self):
        print(f'running {self.n_random_cases} random test cases ... ', end='')
        for ii in range(self.n_random_cases):
            board, hands = deal_random_board_hands(n_hands=8, n_cards=4)
            self._test_best_hand(board, hands)
            if ii % self.print_every_n_cases == 0:
                print(f' {ii} ', end='')

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
                f'Expected {inverse_hand_order[correct_order]}, '
                f'received {inverse_hand_order[test_order]}')
        )

    def _test_both_hand_orders(self, board, hand, correct_order):
        """
        :param board: ([str])
        :param hand: ([str])
        :param correct_order: (int)
        """
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

    def _test_straight(self, board, hand, expected_possible_straights, expected_high_card):
        board_ranks = [r for r, _ in board]
        possible_straights = get_possible_straights(board_ranks)

        tested_not_correct = set(possible_straights) - set(expected_possible_straights)
        correct_not_tested = set(expected_possible_straights) - set(possible_straights)

        incorrect_items = {k: v for k, v in possible_straights if k in tested_not_correct}
        missing_items = {k: v for k, v in expected_possible_straights if k in correct_not_tested}

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
            first=possible_straights,
            second=expected_possible_straights,
            msg=(
                f'Incorrect possible straights on board {board}\n'
                f'Correct: \n'
                f'{json.dumps(json_dumpable_tuple_dict(expected_possible_straights), indent=4)}\n'
                f'Tested: \n'
                f'{json.dumps(json_dumpable_tuple_dict(possible_straights), indent=4)}'
            )
        )
        best_straight = get_best_straight(possible_straights, hand)
        self.assertEqual(best_straight, expected_high_card)
        self._test_both_hand_orders(board, hand, hand_order[STRAIGHT])

    def test_two_boats(self):
        board = ['3d', '2c', '8s', '3h', '3c']
        hand = ['5s', '2h', '8h', '8c']
        test_order, *test_kickers = brute_force_omaha_hi_rank(board, hand)
        calc_order, *calc_kickers = get_hand_strength(board, hand)

        self._test_both_hand_orders(board, hand, hand_order[FULL_HOUSE])
        self.assertEqual(
            first=test_kickers,
            second=calc_kickers,
            msg=(
                f'\n'
                f'Board: {board}\n'
                f'Hand: {hand}\n'
                f'Brute force says {test_kickers[0]} full of {test_kickers[1]}\n'
                f'Speed calc says {calc_kickers[0]} full of {calc_kickers[1]}'
            )
        )

    def test_boat_with_trips_in_hand(self):
        board = ['Ad', 'Jc', '4s', '4c', '4d']
        hand = ['7h', 'Ts', '7c', '7d']
        calc_order, *calc_kickers = get_hand_strength(board, hand)

        self._test_both_hand_orders(board, hand, hand_order[FULL_HOUSE])
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
        self._test_straight(board, hand, expected_possible_straights, 7)

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

    def test_broadway(self):
        board = ['As', '2d', 'Jc', 'Tc', 'Jh']
        hand = ['9h', 'Kh', '2s', 'Qh']
        expected_possible_straights = {
            (12, 13): 14,
        }
        self._test_straight(board, hand, expected_possible_straights, 14)

    def test_many_straight_cards_straight(self):
        board = ['Ts', '7d', '4h', '2c', '5h']
        hand = ['8h', '9c', '8c', '6h']
        expected_possible_straights = {
            (6, 8): 8,
            (3, 6): 7,
            (1, 3): 5,
        }
        self._test_straight(board, hand, expected_possible_straights, 8)

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
