import unittest

from card_utils.deck import cards as DECK_CARDS
from card_utils.games.poker.action import Action
from card_utils.games.poker.community.omaha.plo.game_state import PLOGameState
from card_utils.games.poker.util import deal_random_hands


class PLOGameStateTestCase(unittest.TestCase):
    """ Test basic poker game state logic """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _create_fixed_setup(
        self,
        num_players,
        deck,
        hands,
        boards=None,
        actions=None,
        blinds=None,
        starting_stacks=None,
    ):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param boards:  ([[str]])
        :param actions: ([dict])
        :param blinds: ([int])
        :param starting_stacks: ([int])
        :return: (PLOGameState)
        """
        actions = actions or []

        blinds = blinds or ([1, 2] if num_players > 2 else [2, 1])
        if starting_stacks is None:
            starting_stacks = [200 for _ in range(num_players)]
        self.assertEqual(num_players, len(starting_stacks))

        return PLOGameState.from_action_dicts(
            num_players=num_players,
            deck=deck,
            hands=hands,
            boards=boards,
            starting_stacks=starting_stacks,
            blinds=blinds,
            action_dicts=actions,
        )

    def _create_random_setup(
        self, num_players, actions=None, blinds=None, starting_stacks=None
    ):
        """
        :param num_players: (int)
        :param actions: ([dict])
        :param starting_stacks: ([int])
        :return: (PLOGameState)
        """
        deck, hands = deal_random_hands(n_hands=num_players, n_cards=4)
        return self._create_fixed_setup(
            num_players=num_players,
            deck=deck,
            hands=hands,
            actions=actions,
            blinds=blinds,
            starting_stacks=starting_stacks,
        )

    def _assert_equal_payouts(self, payouts, expected_payouts):
        """
        :param payouts: ({int: float})
        :param expected_payouts: ({int: float})
        """
        for p in set(payouts) - set(expected_payouts):
            expected_payouts[p] = 0

        self.assertEqual(payouts, expected_payouts)

    def test_heads_up_game_initialisation(self):
        """ test seeding the action """
        plo = self._create_random_setup(num_players=2)
        # action starts on the button
        self.assertEqual(plo.action, 1)
        # street 1 is preflop
        self.assertEqual(plo.street, 0)
        # in 1/2 PLO, min raise for first to act should be 2x the blinds
        # but this is heads up, and the button is also the small blind,
        # and hence in for 1 already. This raise would make it 4 total.
        self.assertEqual(plo.min_bet, 3)

    def test_multi_way_initialisation(self):
        """ test seeding the action """
        plo = self._create_random_setup(num_players=8)
        # action starts UTG
        self.assertEqual(plo.action, 2)
        # street 1 is preflop
        self.assertEqual(plo.street, 0)
        # in 1/2 PLO, min raise for first to act should be 2x the blinds
        self.assertEqual(plo.min_bet, 4)

    def test_heads_up_preflop_fold(self):
        """ test whether the action works correctly
            when the button folds immediately heads up preflop
        """
        plo = self._create_random_setup(num_players=2)
        self.assertFalse(plo.is_action_closed())

        self.assertEqual(plo.action, 1)
        plo.append_action(1, Action.action_fold)

        self.assertTrue(plo.is_action_closed())

        plo.advance_action()

        self._assert_equal_payouts(plo.payouts, {0: 3})

    def test_heads_up_postflop_fold(self):
        """
        preflop:  button raises to 4, BB calls
        postflop: BB checks, button bets 4, BB folds

        """
        plo = self._create_random_setup(num_players=2)

        plo.append_action(1, Action.action_raise, amount=3)
        # self.assertFalse(plo.is_action_closed())
        plo.advance_action()

        self.assertEqual(plo.amount_to_call, 2)
        self.assertEqual(plo.action, 0)
        plo.append_action(0, Action.action_call)

        self.assertTrue(plo.is_action_closed())
        self.assertEqual(plo.street, 0)
        plo.advance_action()

        self.assertEqual(plo.street, 1)
        plo.act(0, Action.action_check)
        plo.act(1, Action.action_bet, 4)

        plo.act(0, Action.action_fold)
        self._assert_equal_payouts(plo.payouts, {1: 12})

    def test_heads_up_all_in_preflop(self):
        """
        preflop:  pot-pot-pot-pot-all in-call
                  BB wins with flopped royal flush
        """
        hand_0 = ["As", "Ah", "Ks", "Kh"]
        hand_1 = ["2c", "2d", "2h", "2s"]
        boards = [["Qs", "Js", "Ts"]]
        plo = self._create_fixed_setup(
            num_players=2,
            hands=[hand_0, hand_1],
            boards=boards,
            deck=[c for c in DECK_CARDS if c not in hand_0 + hand_1 + boards[0]],
        )

        plo.act(1, Action.action_raise, amount=plo.max_bet)
        plo.act(0, Action.action_raise, amount=plo.max_bet)
        plo.act(1, Action.action_raise, amount=plo.max_bet)
        plo.act(0, Action.action_raise, amount=plo.max_bet)
        plo.act(1, Action.action_raise, amount=plo.stacks[1])
        plo.act(0, Action.action_call)

        self._assert_equal_payouts(
            payouts=plo.payouts, expected_payouts={0: 400})

    def test_three_way_all_in_preflop(self):
        """ three way all in, small blind wins with flopped royal """
        hand_0 = ["As", "Ah", "Ks", "Kh"]
        hand_1 = ["2c", "2d", "2h", "2s"]
        hand_2 = ["3c", "3d", "3h", "3s"]
        boards = [["Qs", "Js", "Ts"]]
        plo = self._create_fixed_setup(
            num_players=3,
            hands=[hand_0, hand_1, hand_2],
            boards=boards,
            deck=[
                c for c in DECK_CARDS if c not in hand_0 + hand_1 + hand_2 + boards[0]
            ],
        )

        plo.act(2, Action.action_raise, amount=plo.max_bet)
        plo.act(0, Action.action_raise, amount=plo.max_bet)
        plo.act(1, Action.action_raise, amount=plo.max_bet)
        plo.act(2, Action.action_raise, amount=plo.stacks[2])
        plo.act(0, Action.action_call)
        plo.act(1, Action.action_call)

        self._assert_equal_payouts(
            payouts=plo.payouts, expected_payouts={0: 600})

    def test_three_way_river_fold(self):
        """ button pots every street and they fold on the river """

        plo = self._create_random_setup(num_players=3)

        self.assertEqual(plo.street, 0)

        # Preflop
        plo.act(2, Action.action_raise, amount=plo.max_bet)
        plo.act(0, Action.action_call)
        plo.act(1, Action.action_call)

        self.assertEqual(plo.street, 1)

        # Flop
        plo.act(0, Action.action_check)
        plo.act(1, Action.action_check)
        plo.act(2, Action.action_bet, amount=plo.max_bet)
        plo.act(0, Action.action_call)
        plo.act(1, Action.action_call)

        self.assertEqual(plo.street, 2)

        # Turn
        plo.act(0, Action.action_check)
        plo.act(1, Action.action_check)
        plo.act(2, Action.action_bet, amount=plo.max_bet)
        plo.act(0, Action.action_call)
        plo.act(1, Action.action_call)

        self.assertEqual(plo.street, 3)

        # River
        plo.act(0, Action.action_check)
        plo.act(1, Action.action_check)
        plo.act(2, Action.action_bet, amount=plo.stacks[2])
        plo.act(0, Action.action_fold)
        plo.act(1, Action.action_fold)

        self.assertEqual(plo.street, 4)

        self._assert_equal_payouts(
            payouts=plo.payouts, expected_payouts={2: 424})

    def test_eight_way_normal_hand(self):
        """ a reasonable 8-way hand """

        hands = [
            ["7c", "3s", "6s", "3h"],  # [0] SB - folds
            ["Td", "7s", "Jh", "3c"],  # [1] BB - calls
            ["Js", "6d", "2h", "Kh"],  # [2] 5-off - folds
            ["Ah", "6c", "Qs", "Kd"],  # [3] 4-off - raises
            ["Qc", "2s", "7h", "Ks"],  # [4] 3-off - folds
            ["4c", "Jc", "5c", "Ac"],  # [5] Hijack - folds
            ["4d", "Ad", "8s", "6h"],  # [6] Cutoff - folds
            ["8d", "5d", "7d", "Ts"],  # [7] Button - calls
        ]
        boards = [["Kc", "Qh", "Qd", "9d", "3d"]]
        plo = self._create_fixed_setup(
            num_players=8,
            hands=hands,
            boards=boards,
            deck=[
                c
                for c in DECK_CARDS
                if not bool(any(c in h for h in hands) or (c in boards[0]))
            ],
        )

        self.assertEqual(plo.street, 0)

        # Preflop
        plo.act(2, Action.action_fold)
        # min raise for UTG is 2x big blind (4)
        # max raise is calling amount (2) + pot (1 + 2 + 2) = 7
        self.assertEqual(plo.min_bet, 4)
        self.assertEqual(plo.max_bet, 7)
        plo.act(3, Action.action_raise, amount=6)
        # min raise should be at least as big as the last raise,
        # which was 4 = 6 - 2 ==> min raise is 10 all day
        # pot here should be 9 (6 + 2 + 1)
        # so max bet is raising. 6 to call,
        # and 15 + raising 15 on top ==> 21 total
        self.assertEqual(plo.min_bet, 10)
        self.assertEqual(plo.max_bet, 21)
        plo.act(4, Action.action_fold)
        plo.act(5, Action.action_fold)
        plo.act(6, Action.action_fold)
        plo.act(7, Action.action_call)
        plo.act(0, Action.action_fold)
        plo.act(1, Action.action_call)

        self.assertEqual(plo.street, 1)

        # Flop
        plo.act(1, Action.action_check)
        plo.act(3, Action.action_bet, amount=plo.max_bet)
        plo.act(7, Action.action_call)
        plo.act(1, Action.action_call)

        self.assertEqual(plo.street, 2)

        # Turn makes flush for poor button
        plo.act(1, Action.action_check)
        plo.act(3, Action.action_bet, amount=plo.max_bet)
        plo.act(7, Action.action_call)
        plo.act(1, Action.action_fold)

        self.assertEqual(plo.street, 3)

        # River
        plo.act(3, Action.action_bet, amount=plo.stacks[3])
        plo.act(7, Action.action_call)

        self.assertEqual(plo.street, 4)

        self._assert_equal_payouts(
            payouts=plo.payouts, expected_payouts={3: 426})
