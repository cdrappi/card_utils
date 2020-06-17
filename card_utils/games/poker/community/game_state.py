""" class for generic omaha game state """
import logging
import random
from typing import Dict, List

from card_utils.games.poker.action import Action
from card_utils.games.poker.game_state import PokerGameState

logger = logging.getLogger(__name__)


class CommunityGameState(PokerGameState):
    """ basic community card game state """

    # NOTE: override these in subclasses!
    name = "abstract_community"
    num_hole_cards = 0

    # preflop = 0
    # postflop = 1
    # turn = 2
    # river = 3
    showdown_street = 4

    street_names = {0: "PRE-FLOP", 1: "FLOP",
                    2: "TURN", 3: "RIVER", 4: "SHOWDOWN"}

    def __init__(
        self,
        num_players: int,
        deck: List[str],
        starting_stacks: List[int],
        hands: List[List[str]],
        boards: List[List[str]] = None,
        ante: int = 0,
        blinds: List[int] = None,
        stacks: List[int] = None,
        action: int = None,
        street: int = 0,
        actions: List[Dict] = None,
        last_actions: Dict[int, str] = None,
        pot_balances: Dict[int, int] = None,
        all_in_runouts: int = 1,
    ):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param starting_stacks: ([int])
        :param hands: ([[str]])
        :param boards: ([[str]])
        :param ante: (int)
        :param blinds: ([int])
        :param action: (int)
        :param street: (int)
        :param actions: ([dict]) list of dicts like:
            {
                "player": int,
                "action": str,
                "amount": int  [only necessary for bet/call/raises]
            }
        :param last_actions: ({int: str})
        :param pot_balances: ({int: int})
        :param all_in_runouts: (int)
        """
        if boards is None:
            boards = [[]]

        if len(boards) != 1:
            raise ValueError(
                f"{self.name} is a community-card game, "
                f"so it must only have one board"
            )
        for hand in hands:
            if len(hand) != self.num_hole_cards:
                raise ValueError(
                    f"Hands in {self.name} must have exactly "
                    f"{self.num_hole_cards} cards. "
                    f"You provided {len(hand)}\n"
                    f"Perhaps you need to override the num_hole_cards "
                    f"class variable in {self.__class__.__name__}"
                )

        if num_players == 2 and blinds[0] < blinds[1]:
            logger.warning(
                f"Flipping the blinds for 2-handed play. To suppress this warning, "
                f"you should flip the order of blinds in heads up play. "
                f"e.g. input the blinds as [2, 1] rather than [1, 2] "
                f"because the dealer pays the small blind "
                f"and acts second on all later streets"
            )
            blinds = [blinds[1], blinds[0]]

        PokerGameState.__init__(
            self,
            num_players=num_players,
            deck=deck,
            starting_stacks=starting_stacks,
            hands=hands,
            boards=boards,
            ante=ante,
            blinds=blinds,
            stacks=stacks,
            action=action,
            street=street,
            actions=actions,
            last_actions=last_actions,
            pot_balances=pot_balances,
            all_in_runouts=all_in_runouts,
        )

    @property
    def valid_actions(self):
        """ big blind also gets option

        :return: ({str})
        """
        valid_action_set = PokerGameState.valid_actions.fget(self)
        if self.is_acting_last_preflop():
            valid_action_set.add(Action.action_raise)
        return valid_action_set

    @property
    def big_blind_player(self):
        """
        :return: (bool)
        """
        return 0 if self.num_players == 2 else 1

    @property
    def utg_preflop(self):
        """
        In heads-up, player 1 is the button AND the small blind,
        and therefore starts the action before the flop

        Otherwise, the "UTG" player goes first.
        In 3-handed games, this is the dealer

        :return: (int)
        """
        return 1 if self.num_players == 2 else 2

    def is_acting_last_preflop(self):
        """ big blind acts last pre-flop

        :return: (bool)
        """
        return self.street == 0 and self.action == self.big_blind_player

    def order_hands(self, players):
        """ given a list of players who've seen the hand to showdown,
            sort them by their hand strength,
            first on the resulting list having the strongest hands,
            to last on the list with the weakest hand

        :param players: ([int])
        :return: ([[int]])
        """
        raise NotImplementedError(
            f"All CommunityGameState objects must implement order_hands "
            f"to decide who wins at showdown"
        )

    def get_cards_remaining(self) -> int:
        """
        :return: (int)
        """
        return 5 - len(self.board)

    def runout_all_in_board(self, cards_remaining: int):
        """
        :param cards_remaining: (int)
        """
        runout = random.sample(self.deck, cards_remaining)
        self.boards[0] = self.boards[0] + runout

    def reset_all_in_board(self, cards_remaining: int):
        """
        :param cards_remaining: (int)
        """
        self.boards[0] = self.boards[0][0: 5 - cards_remaining]

    def extract_blinds(self):
        """ move blinds from self.stacks to self.pot """
        for player, blind in enumerate(self.blinds):
            amount = min(self.stacks[player], blind)
            self.put_money_in_pot(player, amount)

    def get_starting_action(self):
        """ given self.street_actions, derive the current:
            - street
            - action
            - players who have folded
        """
        if self.street == 0:
            # Pre-flop action begins with UTG (2) except 2-handed
            return self.utg_preflop
        else:
            # Post-flop action always begins with the first player
            # left of the dealer who hasn't folded
            # e.g. small blind (0), then big blind (1)... etc
            return next(p for p in range(self.num_players) if not self.cannot_act(p))

    def move_street(self):
        """ increment the street and then deal out flop/turn/river if necessary """
        PokerGameState.move_street(self)
        if self.action is None:
            # the action is closed because everyone is all in,
            # and we need to deal multiple runouts,
            # and this is persisted back to PokerGameState
            # by setting self.action to None
            return

        if self.street == 1 and not self.flop:
            # Flop
            self.deal_cards_to_board(3)
        elif self.street == 2 and not self.turn:
            # Turn
            self.deal_cards_to_board(1)
        elif self.street == 3 and not self.river:
            # River
            self.deal_cards_to_board(1)

    def deal_cards_to_board(self, n):
        """
        :param n: (int)
        """
        cards = self.deck[0:n]
        self.deck = self.deck[n:]
        self.boards[0].extend(cards)
    
    def should_rake_pot(self) -> bool:
        """ no flop, no drop """
        return bool(self.flop)

    @property
    def board(self):
        """ in community card games, there is only one board,
            so use this property to set/get it

        :return: ([str])
        """
        return self.boards[0]

    @property
    def flop(self):
        """
        :return: ([str])
        """
        return self.board[0:3]

    @property
    def turn(self):
        """
        :return: ([str])
        """
        return self.board[3:4]

    @property
    def river(self):
        """
        :return: ([str])
        """
        return self.board[4:5]

    def player_name(self, player_index):
        """
        :param player_index: (int)
        :return: (str) e.g. 'BIG BLIND', 'BUTTON'
        """
        if not (0 <= player_index < self.num_players):
            raise ValueError(
                f"CommunityGameState.player_name: invalid player_index arg: "
                f"{player_index}"
                f"\n"
                f"Must be 0 <= player_index < num_players"
            )

        if self.num_players == 2:
            return "BUTTON" if player_index == 1 else "BIG BLIND"

        if player_index == 0:
            return "SMALL BLIND"
        elif player_index == 1:
            return "BIG BLIND"
        elif player_index == self.num_players - 1:
            return "BUTTON"
        elif player_index == self.num_players - 2:
            return "CUTOFF"
        elif player_index == self.num_players - 3:
            return "HIJACK"
        else:
            utg_str = f"+{player_index - 2}" if player_index - 2 else ""
            return f"{self.num_players - player_index - 1}-OFF / UTG{utg_str}"

    def state_dict(self, player):
        """ serialise all game state to dictionary
            from the perspective of the input player

        :param player: (int)
        :return: (dict)
        """
        return {
            "player": player,
            "num_players": self.num_players,
            "starting_stacks": self.starting_stacks,
            "hand": self.hands[player],
            "board": self.board,
            "ante": self.ante,
            "blinds": self.blinds,
            "action": self.action,
            "street": self.street,
            "actions": [action.to_dict() for action in self.actions],
            "last_actions": self.last_actions,
            "pot_balances": self.pot.balances,
        }
