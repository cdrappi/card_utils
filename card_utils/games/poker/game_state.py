from typing import List

from card_utils.games.poker.street_action import StreetAction
from card_utils.util import count_in


class PokerGameState:
    """ class for generic poker game state """

    name = 'poker'  # NOTE: override this in subclasses

    def __init__(self,
                 num_players: int,
                 deck: List[str],
                 hands: List[List[str]],
                 stacks: List[int],
                 boards: List[List[str]] = None,
                 pot: int = 0,
                 small_blind: int = 1,
                 big_blind: int = 2,
                 action: int = 0,
                 street: int = 1,
                 street_actions: List[List[StreetAction]] = None):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param stacks: ([[int]])
        :param boards: ([[str]])
        :param pot: (int)
        :param small_blind: (int)
        :param big_blind: (int)
        :param action: (int) the player index who acts (0-indexed)
        :param street: (int) the current street (1-indexed)
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

        if len(stacks) != num_players:
            raise ValueError(
                f'PokerGameState.__init__: '
                f'must have exactly one stack per player'
            )
        self.stacks = stacks

        boards = boards or [[]]
        if len(boards) not in {1, num_players}:
            raise ValueError(
                f'PokerGameState.__init__: (boards)'
                f'must have exactly one board, '
                f'or a board for every player'
            )
        self.boards = boards

        self.pot = pot

        if small_blind > big_blind:
            raise ValueError(
                f'PokerGameState.__init__: '
                f'small blind cannot be less than big blind'
            )
        self.small_blind = small_blind
        self.big_blind = big_blind

        self.action = action
        self.street = street
        self.street_actions = street_actions or []

    def move_action(self):
        """ move action by 1 player """
        self.action = (self.action + 1) % self.num_players

    def is_action_closed(self, street):
        """
        :param street: (int)
        :return: (bool)
        """
        if len(self.street_actions) < street:
            # we haven't even gotten to the street yet
            return False

        last_actions = {}
        for action in self.street_actions[street - 1]:
            last_actions[action.player] = action.action_type

        # action is closed when either:
        values = last_actions.values()
        passes = count_in(values, StreetAction.valid_passes)
        if passes == self.num_players:
            # (1) everyone's last action is in {'PASS', 'CHECK'}
            return True

        closers = count_in(values, StreetAction.valid_closes)
        aggressors = count_in(values, StreetAction.valid_aggressions)

        if aggressors == 1 and closers == self.num_players - 1:
            # (2) everyone's last action is in {'PASS', 'FOLD', 'CALL'}
            #     except one in {'BET', 'RAISE'}
            return True

        return False
