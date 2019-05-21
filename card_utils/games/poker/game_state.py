from typing import List


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

        self.pot = pot

        if small_blind > big_blind:
            raise ValueError(
                f'PokerGameState.__init__: '
                f'small blind cannot be less than big blind'
            )
        self.small_blind = small_blind
        self.big_blind = big_blind
