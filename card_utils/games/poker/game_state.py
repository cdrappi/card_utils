from typing import List

from card_utils.games.poker.street_action import StreetAction
from card_utils.util import count_in


class PokerGameState:
    """ class for generic poker game state """

    # NOTE: override this in subclasses
    name = 'abstract_poker'

    def __init__(self,
                 num_players: int,
                 deck: List[str],
                 hands: List[List[str]],
                 starting_stacks: List[int],
                 boards: List[List[str]] = None,
                 ante: int = 0,
                 blinds: List[int] = None,
                 big_blind: int = 2,
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

        self.pots = {}
        self.action = 0
        self.street = 1
        self.players_folded = set()
        self.street_to_actions = {}
        self.reset_state_from_street_actions()

    @staticmethod
    def get_starting_action():
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
        return 0

    def extract_antes(self):
        """ subtract antes from stacks and
            return total amount extracted

        :return: (int) total antes
        """
        antes = 0
        for player_index in range(self.num_players):
            if self.stacks[player_index] >= self.ante:
                self.stacks[player_index] -= self.ante
                antes += self.ante
            else:
                # TODO: side pots nooooooo
                raise Exception('TODO: implement side pots!')

        return antes

    def extract_blinds(self):
        """
        :return: (int) total blinds
        """
        blinds = 0
        for player_index, blind in enumerate(self.blinds):
            if self.stacks[player_index] >= blind:
                self.stacks[player_index] -= blind
                blinds += blind
            else:
                # TODO: side pots nooooooo
                raise Exception('TODO: implement side pots!')
        return blinds

    def extract_antes_and_blinds(self):
        """ subtract antes/blinds from stacks and
            return total amount extracted

        :return: (int) amount extracted
        """
        # TODO: needs to be a dict....
        return self.extract_antes() + self.extract_blinds()

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
        self.street = 1
        self.action = self.get_starting_action()
        self.players_folded = set()
        self.street_to_actions = {}
        self.pots = self.extract_antes_and_blinds()

        for street_action in self.street_actions:
            street = street_action.street
            action = street_action.action

            if street not in self.street_to_actions:
                self.street_to_actions[street] = []

            if action != self.action:
                raise Exception(
                    f'The action is on {self.action}, but the next '
                    f'StreetAction object comes from {action}'
                )

            if street_action.action == StreetAction.action_fold:
                self.players_folded.add(street_action.player)

            self.street_to_actions[street].append(street_action)
            self.move_action()

        # TODO
        pass

    def increment_action(self):
        """ move the action to the left by one,
            irrespective of whether that player has already folded
        """
        self.action = (self.action + 1) % self.num_players

    def move_action(self):
        """ move action by 1 player """
        # TODO
        self.increment_action()
        while self.action not in self.players_folded:
            self.increment_action()

    def is_action_closed(self, street):
        """
        :param street: (int)
        :return: (bool)
        """
        # TODO
        if len(self.street_actions) < street:
            # we haven't even gotten to the street yet
            return False

        n_street_players = len(self.players_starting_street[street - 1])

        last_actions = {}
        for action in self.street_actions[street - 1]:
            last_actions[action.player] = action.action_type

        # action is closed when either:
        values = last_actions.values()
        passes = count_in(values, StreetAction.valid_passes)
        if passes == n_street_players:
            # (1) everyone's last action is in {'PASS', 'CHECK'}
            return True

        closers = count_in(values, StreetAction.valid_closes)
        aggressors = count_in(values, StreetAction.valid_aggressions)

        if aggressors == 1 and closers == n_street_players - 1:
            # (2) everyone's last action is in {'PASS', 'FOLD', 'CALL'}
            #     except one in {'BET', 'RAISE'}
            return True

        return False
