""" class for generic omaha game state """
from typing import List, Dict

from card_utils.games.poker.game_state import PokerGameState
from card_utils.games.poker.street_action import StreetAction


class CommunityGameState(PokerGameState):
    """ basic community card game state """

    # NOTE: override these in subclasses!
    name = 'abstract_community'
    num_hole_cards = 0

    max_streets = 7

    def __init__(self,
                 num_players: int,
                 deck: List[str],
                 hands: List[List[str]],
                 starting_stacks: List[int],
                 boards: List[List[str]] = None,
                 ante: int = 0,
                 blinds: List[int] = None,
                 street_actions: List[Dict] = None,
                 ):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param starting_stacks: ([[int]])
        :param boards: ([[str]])
        :param blinds: ([int])
        :param street_actions: ([dict])
        """
        if len(boards) != 1:
            raise ValueError(
                f'{self.name} is a community-card game, '
                f'so it must only have one board'
            )
        for hand in hands:
            if len(hand) != self.num_hole_cards:
                raise ValueError(
                    f'Hands in {self.name} must have exactly '
                    f'{self.num_hole_cards}\n'
                    f'Perhaps you need to override the num_hole_cards '
                    f'class variable in {self.__class__.__name__}'
                )

        super().__init__(
            num_players=num_players,
            deck=deck,
            hands=hands,
            starting_stacks=starting_stacks,
            boards=boards,
            ante=ante,
            blinds=blinds,
            street_actions=street_actions,
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
            f'All CommunityGameState objects must implement order_hands '
            f'to decide who wins at showdown'
        )

    def get_starting_action(self):
        """ given self.street_actions, derive the current:
            - street
            - action
            - players who have folded
        """
        if self.street == 1:
            # Pre-flop action begins with UTG (2) except 2-handed
            return (
                # In heads-up, player 1 is the button AND the small blind,
                # and therefore starts the action before the flop
                1 if self.num_players == 2
                # Otherwise, the "UTG" player goes first.
                # In 3-handed games, this is the dealer
                else 2
            )
        else:
            # Post-flop action always begins with the first player
            # left of the dealer who hasn't folded
            # e.g. small blind (0), then big blind (1)... etc
            return next(
                p for p in range(self.num_players)
                if self.last_actions.get(p) == StreetAction.action_fold
            )

    @property
    def board(self):
        """ in community card games, there is only one board,
            so use this property to set/get it

        :return: ([str])
        """
        return self.boards[0]
