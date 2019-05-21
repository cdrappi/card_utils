""" class for generic omaha game state """
from typing import List

from card_utils.games.poker.game_state import PokerGameState
from card_utils.games.poker.street_action import StreetAction


class CommunityGameState(PokerGameState):
    """ basic community card game state """

    # NOTE: override these in subclasses!
    name = 'community_card_poker'
    num_hole_cards = 0

    def __init__(self,
                 num_players: int,
                 deck: List[str],
                 hands: List[List[str]],
                 stacks: List[int],
                 boards: List[List[str]] = None,
                 pot: int = 0,
                 small_blind: int = 1,
                 big_blind: int = 2,
                 action: int = None,
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
            --> if None, default is set based on number of players
        :param street: (int) the current street (1-indexed)
        :param street_actions: ([[int]])
            Each street gets a list of list of actions,
            represented by an object StreetAction
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

        if action is None:
            action = (
                # In heads-up, player 1 is the button AND the small blind,
                # and therefore starts the action before the flop
                0 if num_players == 2
                # Otherwise, the "UTG" player goes first.
                # In 3-handed games, this is the dealer
                else 2
            )

        super().__init__(
            num_players=num_players,
            deck=deck,
            hands=hands,
            stacks=stacks,
            boards=boards,
            pot=pot,
            small_blind=small_blind,
            big_blind=big_blind,
            action=action,
            street=street,
            street_actions=street_actions,
        )
