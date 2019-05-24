import unittest

from card_utils.games.poker.action import Action
from card_utils.games.poker.community.omaha.plo.game_state import PLOGameState
from card_utils.games.poker.util import deal_random_hands


class PLOGameStateTestCase(unittest.TestCase):
    """ Test basic poker game state logic """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _create_random_setup(self, num_players,
                             actions=None,
                             blinds=None,
                             starting_stacks=None):
        """
        :param num_players: (int)
        :param actions: ([dict])
        :param starting_stacks: ([int])
        :return: (PLOGameState)
        """
        actions = actions or []

        blinds = blinds or ([1, 2] if num_players > 2 else [2, 1])
        if starting_stacks is None:
            starting_stacks = [200 for _ in range(num_players)]

        self.assertEqual(num_players, len(starting_stacks))

        deck, hands = deal_random_hands(n_hands=num_players, n_cards=4)
        return PLOGameState(
            num_players=num_players,
            deck=deck,
            hands=hands,
            starting_stacks=starting_stacks,
            blinds=blinds,
            actions=actions
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
        self.assertEqual(plo.street, 1)

    def test_multi_way_initialisation(self):
        """ test seeding the action """
        plo = self._create_random_setup(num_players=8)
        # action starts UTG
        self.assertEqual(plo.action, 2)
        # street 1 is preflop
        self.assertEqual(plo.street, 1)

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
        self.assertTrue(plo.is_all_action_complete)

        self._assert_equal_payouts(plo.payouts, {0: 3})

    def test_heads_up_postflop_fold(self):
        """
        preflop:  button raises to 4, BB calls
        postflop: BB checks, button bets 4, BB folds

        """
        plo = self._create_random_setup(num_players=2)

        plo.append_action(1, Action.action_raise, amount=4)
        self.assertEqual(plo.amount_to_call, 2)
        plo.append_action(0, Action.action_call, amount=plo.amount_to_call)

        self.assertTrue(plo.is_action_closed())

        plo.advance_action()
        self.assertTrue(plo.is_all_action_complete)

        self._assert_equal_payouts(plo.payouts, {0: 3})
