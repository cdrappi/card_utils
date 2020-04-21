import unittest

from card_utils.deck import cards as DECK_CARDS
from card_utils.games.poker.action import Action
from card_utils.games.poker.community.holdem.nl.game_state import NLHEGameState
from card_utils.games.poker.util import deal_random_hands


class NLHEGameStateTestCase(unittest.TestCase):
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
        :return: (NLHEGameState)
        """
        actions = actions or []

        blinds = blinds or ([1, 2] if num_players > 2 else [2, 1])
        if starting_stacks is None:
            starting_stacks = [200 for _ in range(num_players)]
        self.assertEqual(num_players, len(starting_stacks))

        return NLHEGameState.from_action_dicts(
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
        :return: (NLHEGameState)
        """
        deck, hands = deal_random_hands(n_hands=num_players, n_cards=2)
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

    def test_heads_up_all_in_preflop(self):
        """
        preflop:  pot-pot-pot-pot-all in-call
                  BB wins with flopped royal flush
        """
        hand_0 = ["As", "Ks"]
        hand_1 = ["2c", "2d"]
        boards = [["Qs", "Js", "Ts"]]
        nlhe = self._create_fixed_setup(
            num_players=2,
            hands=[hand_0, hand_1],
            boards=boards,
            deck=[c for c in DECK_CARDS if c not in hand_0 + hand_1 + boards[0]],
        )

        nlhe.act(1, Action.action_raise, amount=nlhe.max_bet)
        nlhe.act(0, Action.action_raise, amount=nlhe.max_bet)
        nlhe.act(1, Action.action_raise, amount=nlhe.max_bet)
        nlhe.act(0, Action.action_raise, amount=nlhe.max_bet)
        nlhe.act(1, Action.action_raise, amount=nlhe.stacks[1])
        nlhe.act(0, Action.action_call)

        self._assert_equal_payouts(
            payouts=nlhe.payouts, expected_payouts={0: 400})

    def test_three_way_all_in_preflop(self):
        """ three way all in, small blind wins with flopped royal """
        hand_0 = ["As", "Ks"]
        hand_1 = ["2c", "2d"]
        hand_2 = ["3c", "3d"]
        boards = [["Qs", "Js", "Ts"]]
        nlhe = self._create_fixed_setup(
            num_players=3,
            hands=[hand_0, hand_1, hand_2],
            boards=boards,
            deck=[
                c for c in DECK_CARDS if c not in hand_0 + hand_1 + hand_2 + boards[0]
            ],
        )

        nlhe.act(2, Action.action_raise, amount=nlhe.max_bet)
        nlhe.act(0, Action.action_raise, amount=nlhe.max_bet)
        nlhe.act(1, Action.action_raise, amount=nlhe.max_bet)
        nlhe.act(2, Action.action_raise, amount=nlhe.stacks[2])
        nlhe.act(0, Action.action_call)
        nlhe.act(1, Action.action_call)

        self._assert_equal_payouts(
            payouts=nlhe.payouts, expected_payouts={0: 600})

    def test_three_way_river_fold(self):
        """ button pots every street and they fold on the river """

        nlhe = self._create_random_setup(num_players=3)

        self.assertEqual(nlhe.street, 0)

        # Preflop
        nlhe.act(2, Action.action_raise, amount=nlhe.max_bet)
        nlhe.act(0, Action.action_call)
        nlhe.act(1, Action.action_call)

        self.assertEqual(nlhe.street, 1)

        # Flop
        nlhe.act(0, Action.action_check)
        nlhe.act(1, Action.action_check)
        nlhe.act(2, Action.action_bet, amount=nlhe.max_bet)
        nlhe.act(0, Action.action_call)
        nlhe.act(1, Action.action_call)

        self.assertEqual(nlhe.street, 2)

        # Turn
        nlhe.act(0, Action.action_check)
        nlhe.act(1, Action.action_check)
        nlhe.act(2, Action.action_bet, amount=nlhe.max_bet)
        nlhe.act(0, Action.action_call)
        nlhe.act(1, Action.action_call)

        self.assertEqual(nlhe.street, 3)

        # River
        nlhe.act(0, Action.action_check)
        nlhe.act(1, Action.action_check)
        nlhe.act(2, Action.action_bet, amount=nlhe.stacks[2])
        nlhe.act(0, Action.action_fold)
        nlhe.act(1, Action.action_fold)

        self.assertEqual(nlhe.street, 4)

        self._assert_equal_payouts(
            payouts=nlhe.payouts, expected_payouts={2: 424})

    def test_eight_way_normal_hand(self):
        """ a reasonable 8-way hand """

        hands = [
            ["7c", "3s"],  # [0] SB - folds
            ["Td", "7s"],  # [1] BB - calls
            ["Js", "6d"],  # [2] 5-off - folds
            ["Qs", "Kd"],  # [3] 4-off - raises: will make boat and win
            ["7h", "Ks"],  # [4] 3-off - folds
            ["5c", "Ac"],  # [5] Hijack - folds
            ["8s", "6h"],  # [6] Cutoff - folds
            ["8d", "7d"],  # [7] Button - calls: fill make flush and stack off
        ]
        boards = [["Kc", "Qh", "Qd", "9d", "3d"]]
        nlhe = self._create_fixed_setup(
            num_players=8,
            hands=hands,
            boards=boards,
            deck=[
                c
                for c in DECK_CARDS
                if not bool(any(c in h for h in hands) or (c in boards[0]))
            ],
        )

        self.assertEqual(nlhe.street, 0)

        # Preflop
        nlhe.act(2, Action.action_fold)
        nlhe.act(3, Action.action_raise, amount=6)
        nlhe.act(4, Action.action_fold)
        nlhe.act(5, Action.action_fold)
        nlhe.act(6, Action.action_fold)
        nlhe.act(7, Action.action_call)
        nlhe.act(0, Action.action_fold)
        nlhe.act(1, Action.action_call)

        self.assertEqual(nlhe.street, 1)

        # Flop
        nlhe.act(1, Action.action_check)
        nlhe.act(3, Action.action_bet, amount=nlhe.max_bet)
        nlhe.act(7, Action.action_call)
        nlhe.act(1, Action.action_call)

        self.assertEqual(nlhe.street, 2)

        # Turn makes flush for poor button
        nlhe.act(1, Action.action_check)
        nlhe.act(3, Action.action_bet, amount=nlhe.max_bet)
        nlhe.act(7, Action.action_call)
        nlhe.act(1, Action.action_fold)

        self.assertEqual(nlhe.street, 3)

        # River
        nlhe.act(3, Action.action_bet, amount=nlhe.stacks[3])
        nlhe.act(7, Action.action_call)

        self.assertEqual(nlhe.street, 4)

        self._assert_equal_payouts(
            payouts=nlhe.payouts, expected_payouts={3: 426})
