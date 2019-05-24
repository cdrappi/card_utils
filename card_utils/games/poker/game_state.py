from typing import List, Dict

from card_utils.games.poker.action import Action
from card_utils.games.poker.pot import Pot


class PokerGameState:
    """ class for generic poker game state """

    # NOTE: override this in subclasses
    name = 'abstract_poker'
    max_streets = 0

    def __init__(self,
                 num_players: int,
                 deck: List[str],
                 hands: List[List[str]],
                 starting_stacks: List[int],
                 boards: List[List[str]] = None,
                 ante: int = 0,
                 blinds: List[int] = None,
                 actions: List[Dict] = None,
                 ):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param starting_stacks: ([[int]])
        :param boards: ([[str]])
        :param ante: (int)
        :param blinds: ([int])
        :param actions: ([dict]) list of dicts like:
            {
                "player": int,
                "action": str,
                "amount": int  [only necessary for bet/call/raises]
            }
        """
        if num_players < 2:
            raise ValueError(
                f'Fundamentally, poker is a game of more than 1 player'
                f'\n'
                f'{self.__class__.__name__} '
                f'was instantiated with {num_players} players'
            )
        self.num_players = num_players

        self.deck = deck

        if len(hands) != num_players:
            raise ValueError(
                f'PokerGameState.__init__: (hands)'
                f'must have exactly one hand per player'
            )
        self.hands = hands

        if len(starting_stacks) != num_players:
            raise ValueError(
                f'PokerGameState.__init__: '
                f'must have exactly one starting stack per player'
            )
        self.stacks = starting_stacks

        boards = boards or [[]]
        if len(boards) not in {1, num_players}:
            raise ValueError(
                f'PokerGameState.__init__: (boards)'
                f'must have exactly one board, '
                f'or a board for every player'
            )
        self.boards = boards

        self.ante = ante
        self.blinds = blinds or []

        self.actions = []
        self.pot = Pot(self.num_players)
        self.last_actions = {}
        self.payouts = {}
        self.action = 0
        self.street = 1
        self.reset_state_from_actions(actions)

    def get_starting_action(self):
        """ the player who starts the action
            on the very first street

            NOTE: override this in specific games.

            examples:
              - for community card games, it's UTG (2) on street 1,
                except when it's 2-handed, when it's the button (1).
                post-flop, its the lowest index player who hasn't folded
              - for stud games, it's the bring on street 1,
                and the player with the best board afterwards

        :return: (int)
        """
        raise NotImplementedError(
            f'NotImplementedError in {self.__class__.__name__}: '
            f'You must override get_starting_action '
            f'in subclasses of PokerGameState'
        )

    def order_hands(self, players):
        """ given a list of players who've seen the hand to showdown,
            sort them by their hand strength,
            first on the resulting list having the strongest hands,
            to last on the list with the weakest hand

        :param players: ([int])
        :return: ([[int]])
        """
        raise NotImplementedError(
            f'All PokerGameState objects must implement order_hands '
            f'to decide who wins at showdown'
        )

    def is_all_in(self, player):
        """
        :param player: (int)
        :return: (bool)
        """
        return self.stacks[player] == 0

    def put_money_in_pot(self, player, amount):
        """
        :param player: (int)
        :param amount: (int)
        """
        if amount > self.stacks[player]:
            raise Exception(
                f'player {player} only has {self.stacks[player]} chips, '
                f'but trying to put {amount} in pot'
            )
        self.stacks[player] -= amount
        self.pot.put_money_in(player, amount)

    def extract_antes(self):
        """ subtract antes from stacks and
            return total amount extracted

        :return: (int) total antes
        """
        for player in range(self.num_players):
            amount = min(self.stacks[player], self.ante)
            self.put_money_in_pot(player, amount)

    def extract_blinds(self):
        """ move blinds from self.stacks to self.pot """
        for player, blind in enumerate(self.blinds):
            amount = min(self.stacks[player], blind)
            self.put_money_in_pot(player, amount)

    def extract_antes_and_blinds(self):
        """ subtract antes/blinds from stacks and
            return total amount extracted

        :return: (int) amount extracted
        """
        self.extract_antes()
        self.extract_blinds()

    def reset_state_from_actions(self, actions):
        """ given self.street_actions, derive the current:
            - pot size
            - street
            - action
            - players who have folded
            - street-to-actions mapping (int --> [StreetAction])

        this method is idempotent, and can always be called
        to set these four helper state variables given
        the list of StreetAction objects
        """
        self.pot = Pot(self.num_players)
        self.last_actions = {}
        self.payouts = {}
        self.extract_antes_and_blinds()
        self.street = 1
        self.action = self.get_starting_action()

        for action_dict in actions:
            self.act(**action_dict)

    def act(self, player, action, amount=None):
        """ create an action, update state and advance the game forward

        :param player: (int)
        :param action: (str)
        :param amount: (int) if None, construct default
        """
        self.append_action(player, action, amount=amount)
        self.advance_action()

    def append_action(self, player, action, amount=None):
        """
        :param player: (int)
        :param action: (str)
        :param amount: (int)
        """
        action_obj = self.build_action(player, action, amount=amount)
        self.validate_action(action_obj)
        self.actions.append(action_obj)
        self.update_state_with_action(action_obj)

    def build_action(self, player, action, amount):
        """
        :param player: (int)
        :param action: (str)
        :param amount: (int)
        :return: (Action)
        """
        if amount is None:
            if action == Action.action_call:
                amount = self.amount_to_call
            elif action in Action.zeros:
                amount = 0
            else:
                raise ValueError(
                    f'Amount cannot be None for action type {action}'
                )

        return Action(
            player=player,
            action=action,
            amount=amount
        )

    def validate_action(self, action):
        """
        :param action: (Action)
        """
        if action.player != self.action:
            raise Exception(
                f'The calculated action is on {self.action}, but '
                f'the next Action object comes from '
                f'{action.player}'
            )

        if self.amount_to_call == 0:
            if action.action in Action.nonzero_to_call:
                raise ValueError(
                    f'it is 0 to call, so {action.action} '
                    f'is an invalid action'
                )
        else:
            if action.action in Action.zero_to_call:
                raise ValueError(
                    f'it is {self.amount_to_call} to call, '
                    f'so {action.action} is an invalid action'
                )

        if self.stacks[action.player] < action.amount:
            raise Exception(
                f'Player {action.player} only has '
                f'{self.stacks[action.player]} in stack, '
                f'less than the desired wager of {action.amount}'
            )

        if action.action in Action.aggressions:
            if self.min_bet is not None and action.amount < self.min_bet:
                raise ValueError(
                    f'Invalid {action.action} size: '
                    f'amount {action.amount} '
                    f'is less than the minimum of {self.min_bet}'
                )

        if action.action in Action.aggressions:
            if self.max_bet is not None and action.amount > self.max_bet:
                raise ValueError(
                    f'Invalid {action.action} size: '
                    f'amount {action.amount} '
                    f'is greater than the limit of {self.max_bet}'
                )

    def update_state_with_action(self, action):
        """
        :param action: (Action)
        :return:
        """
        if action.action in Action.wagers:
            self.put_money_in_pot(
                player=action.player,
                amount=action.amount
            )

        self.last_actions[action.player] = action.action

    def advance_action(self):
        """ move action forward and check if hand is over """
        is_action_closed = self.is_action_closed()

        if not is_action_closed:
            self.move_action()
        else:
            while self.is_action_closed() and self.street <= self.max_streets:
                self.move_street()

        if self.street > self.max_streets:
            self.payouts = self.get_payouts()

    def get_payouts(self):
        """ sort hands and ship Pot

        :return: ({int: int}) player index --> payout
        """
        players_at_showdown = [
            player
            for player in range(self.num_players)
            if self.last_actions.get(player) != Action.action_fold
        ]
        winners = (
            self.order_hands(players_at_showdown)
            if len(players_at_showdown) > 1
            # if everyone's folded, no need to order hands
            else [players_at_showdown]
        )
        payouts = self.pot.settle_showdown(winners)
        return payouts

    def cannot_act(self, player):
        """
        :param player: (int)
        :return: (bool)
        """
        return bool(
            self.is_all_in(player)
            or self.last_actions.get(player) == Action.action_fold
        )

    def mod_n(self, player):
        """
        :param player: (int)
        :return: (int)
        """
        return player % self.num_players

    def get_next_action(self):
        """
        :return: (int)
        """
        return self.mod_n(self.action + 1)

    def increment_action(self):
        """ move the action to the left by one,
            irrespective of whether that player has already folded
        """
        self.action = self.get_next_action()

    def move_action(self):
        """ move action by 1 player """
        self.increment_action()
        while self.cannot_act(self.action):
            self.increment_action()

    def move_street(self):
        """ increment the street, and reset the last_action of
            everyone who hasn't folded
        """
        self.street += 1
        self.last_actions = {
            player: Action.action_fold
            for player, action in self.last_actions.items()
            if action == Action.action_fold
        }
        self.action = self.get_starting_action()

    def everyone_folded_or_all_in(self):
        """ whether all action is closed for all streets

        This only happens in one case:
            Everyone except one person has either:
                - folded
                - went all in

        :return: (bool)
        """
        # TODO: delete?
        n_cant_act = sum(self.cannot_act(p) for p in range(self.num_players))
        return n_cant_act == self.num_players - 1

    def is_action_closed(self):
        """ whether the action is closed for a particular street

        :return: (bool)
        """
        folders = 0
        checkers = 0
        all_in_last_street = 0
        not_yet_acted = 0
        not_all_in_set = set()

        players_in_action_order = (
            self.mod_n(self.action + p)
            for p in range(self.num_players)
        )

        for player in players_in_action_order:
            last_action = self.last_actions.get(player)
            is_all_in = self.is_all_in(player)

            if last_action != Action.action_fold and not is_all_in:
                not_all_in_set.add(player)

            if last_action is None and is_all_in:
                all_in_last_street += 1
            elif last_action is None:
                not_yet_acted += 1
            elif last_action == Action.action_fold:
                folders += 1
            elif last_action == Action.action_check:
                checkers += 1

        not_all_in_balances = {self.pot.balances[p] for p in not_all_in_set}
        if len(not_all_in_balances) > 1:
            # if those who are not all in but have not folded
            # have different balances, then we action is not complete
            return False

        # print(
        #     f'folders={folders}\n'
        #     f'checkers={checkers}\n'
        #     f'aggr_not_all_in={aggr_not_all_in}\n'
        #     f'all_in_last_street={all_in_last_street}\n'
        #     f'not_yet_acted={not_yet_acted}\n'
        #     f'{"-" * 10}'
        # )

        if folders == self.num_players - 1:
            # Case 1: everyone folds except 1 person
            return True

        if folders + checkers + all_in_last_street == self.num_players:
            # Case 2: no one this street has made any bets,
            # and everyone had either folded or went all on a previous street,
            # or checked on this street
            return True

        everyone_closed_last_aggression = (
            # Case 3:
            # Everyone must have acted and not checked
            checkers + not_yet_acted == 0
            # and those who are not all in have all put
            # an equal amount in the pot as the person
            # who has put the most in the pot
            and len({*not_all_in_balances, max(self.pot.balances.values())}) == 1
        )
        return everyone_closed_last_aggression

    @property
    def amount_to_call(self):
        """
        :return: (int)
        """
        return max(self.pot.balances.values()) - self.pot.balances[self.action]

    @property
    def min_bet(self):
        """ in general, the min bet will be the biggest blind
            and the minimum raise will be the difference
            between the last two raises

        :return: (int|None)
        """
        *_, second_highest, highest = sorted(self.pot.balances.values())
        last_raise = highest - second_highest
        biggest_blind = max(self.blinds)
        return max(biggest_blind, last_raise)

    @property
    def max_bet(self):
        """
        :return: (int)
        """
        return self.stacks[self.action]
