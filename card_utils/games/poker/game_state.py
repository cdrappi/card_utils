from typing import List

from card_utils.games.poker.pot import Pot
from card_utils.games.poker.street_action import StreetAction


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
                 street_actions: List[StreetAction] = None,
                 ):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param starting_stacks: ([[int]])
        :param boards: ([[str]])
        :param ante: (int)
        :param blinds: ([int])
        :param street_actions: ([[int]])
            Each street gets a list of list of actions,
            represented by an object StreetAction
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

        self.street_actions = street_actions or []

        self.pot = Pot(self.num_players)
        self.is_all_action_closed = False
        self.last_actions = {}
        self.payouts = {}
        self.action = 0
        self.street = 1
        self.reset_state_from_street_actions()

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
            first on the resulting list having the strongest hand,
            to last on the list with the weakest hand

        :param players: ([int])
        :return: ([int])
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

    def reset_state_from_street_actions(self):
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
        self.is_all_action_closed = False
        self.last_actions = {}
        self.payouts = {}
        self.extract_antes_and_blinds()
        self.street = 1
        self.action = self.get_starting_action()

        for street_action in self.street_actions:

            if street_action.action != self.action:
                raise Exception(
                    f'The calculated action is on {self.action}, but '
                    f'the next StreetAction object comes from '
                    f'{street_action.action}'
                )
            if street_action.street != self.street:
                raise Exception(
                    f'The calculated street is {self.street}, but '
                    f'the next StreetAction object comes from '
                    f'{street_action.street}'
                )

            self.register_street_action(street_action)

    def register_street_action(self, street_action):
        """
        :param street_action: (StreetAction)
        """
        if street_action.action in street_action.valid_wagers:
            self.put_money_in_pot(
                player=street_action.player,
                amount=street_action.amount
            )

        self.last_actions[street_action.player] = street_action.action
        self.move_action()
        if self.is_action_closed():
            if self.street < self.max_streets:
                self.move_street()
            else:
                self.is_all_action_closed = True

        if self.is_all_action_closed:
            self.payouts = self.get_payouts()

    def get_payouts(self):
        """ sort hands and ship Pot

        :return: ({int: int}) player index --> payout
        """
        players_at_showdown = [
            player
            for player in range(self.num_players)
            if self.last_actions[player] != StreetAction.action_fold
        ]
        winners = self.order_hands(players_at_showdown)
        payouts = self.pot.settle_showdown(winners)
        return payouts

    def cannot_act(self, player):
        """
        :param player: (int)
        :return: (bool)
        """
        return bool(
            self.is_all_in(player)
            or self.last_actions.get(player) == StreetAction.action_fold
        )

    def increment_action(self):
        """ move the action to the left by one,
            irrespective of whether that player has already folded
        """
        self.action = (self.action + 1) % self.num_players

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
            player: StreetAction.action_fold
            for player, action in self.last_actions.items()
            if action == StreetAction.action_fold
        }

    def is_action_closed(self):
        """
        :return: (bool)
        """
        folders = 0
        checkers = 0
        callers = 0
        aggr_all_in = 0
        aggr_not_all_in = 0
        all_in_last_street = 0

        for player in range(self.num_players):
            last_action = self.last_actions.get(player)
            is_all_in = self.is_all_in(player)

            if last_action is None and is_all_in:
                all_in_last_street += 1
            elif last_action == StreetAction.action_fold:
                folders += 1
            elif last_action == StreetAction.action_check:
                checkers += 1
            elif last_action == StreetAction.action_call:
                callers += 1
            elif last_action in StreetAction.valid_aggressions:
                if is_all_in:
                    aggr_all_in += 1
                else:
                    aggr_not_all_in += 1

        if folders + checkers + all_in_last_street == self.num_players:
            # Case 1: no one this street has made any bets,
            # and everyone had either folded or went all on a previous street,
            # or checked on this street
            return True

        # Case 2:
        # At most one person's last action was a not-all-in bet or raise
        # And no one's last action can be check
        non_checkers = (
            folders
            + all_in_last_street
            + callers
            + aggr_all_in
            + aggr_not_all_in
        )
        if aggr_not_all_in <= 1 and non_checkers == self.num_players:
            return True

        return False
