""" class for generic omaha game state """
from typing import List

from card_utils.games.poker.game_state import PokerGameState


class CommunityGameState(PokerGameState):
    """ basic community card game state """

    name = 'community_card_poker'
    num_hole_cards = 0  # override this in subclasses!

    def __init__(self,
                 num_players: int,
                 deck: List[str],
                 hands: List[List[str]],
                 stacks: List[int],
                 boards: List[List[str]] = None,
                 pot: int = 0,
                 small_blind: int = 1,
                 big_blind: int = 2):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param stacks: ([[int]])
        :param boards: ([[str]])
        :param pot: (int)
        :param small_blind: (int)
        :param big_blind: (int)
        """
        if len(boards) != 1:
            raise ValueError(
                f'This is a community-card game, '
                f'so it must only have one board'
            )

        for hand in hands:
            if len(hand) != self.num_hole_cards:
                raise ValueError(
                    f'Community card hands must have exactly '
                    f'{self.num_hole_cards}\n'
                    f'Perhaps you need to override the num_hole_cards '
                    f'class variable in {self.__class__.__name__}'
                )

        super().__init__(
            num_players=num_players,
            deck=deck,
            hands=hands,
            stacks=stacks,
            boards=boards,
            pot=pot,
            small_blind=small_blind,
            big_blind=big_blind
        )
