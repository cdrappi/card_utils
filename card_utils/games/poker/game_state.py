from typing import Dict, List

from card_utils.games.poker.action import Action
from card_utils.games.poker.pot import Pot
from card_utils.games.poker.util import is_action_closed


class PokerGameState:
    """ class for generic poker game state """

    # NOTE: override this in subclasses
    name = "abstract_poker"
    showdown_street = 0

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
        actions: List[Action] = None,
        action_dicts: List[Dict] = None,
        last_actions: Dict[int, str] = None,
        pot_balances: Dict[int, int] = None,
        all_in_runouts: int = 1,
        rake_fraction: float = 0.0,
        max_rake: int = 0,
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
        :param rake_fraction: (float)
        :param max_rake: (int)
        """
        if num_players < 2:
            raise ValueError(
                f"Fundamentally, poker is a game of more than 1 player"
                f"\n"
                f"{self.__class__.__name__} "
                f"was instantiated with {num_players} players"
            )
        self.num_players = num_players

        self.deck = deck

        if len(hands) != num_players:
            raise ValueError(
                "PokerGameState.__init__: (hands)"
                "must have exactly one hand per player"
            )
        self.hands = hands

        if len(starting_stacks) != num_players:
            raise ValueError(
                "PokerGameState.__init__: "
                "must have exactly one starting stack per player"
            )
        self.starting_stacks = starting_stacks
        self.stacks = stacks or [s for s in starting_stacks]

        boards = boards or [[]]
        if len(boards) not in {1, num_players}:
            raise ValueError(
                "PokerGameState.__init__: (boards)"
                "must have exactly one board, "
                "or a board for every player"
            )
        self.boards = boards

        blinds = blinds or []
        if not (ante or any(blinds)):
            raise ValueError(
                "There must be either an ante or blinds to play poker"
            )
        self.ante = ante
        self.blinds = blinds

        self.last_actions = last_actions or {}
        self.all_in_runouts = all_in_runouts

        if actions and action_dicts:
            raise ValueError(
                "can only provide either action or action_dicts "
                "to initialise poker game state, not both"
            )
        elif action_dicts:
            actions = [Action(**ad) for ad in action_dicts]
        self.actions = actions or []
        self.rake_fraction = rake_fraction
        self.max_rake = max_rake
    
        self.pot = Pot(
            num_players=self.num_players,
            rake_fraction=rake_fraction,
            max_rake=max_rake,
            balances=pot_balances
        )

        self.street = street

        if action is None:
            self.extract_antes_and_blinds()
            action = self.get_starting_action()

        self.action = action

        self.payouts = {}
        self.rake_paid = {}
        self.is_complete = False

    @classmethod
    def from_action_dicts(
        cls,
        num_players: int,
        deck: List[str],
        hands: List[List[str]],
        starting_stacks: List[int],
        boards: List[List[str]] = None,
        ante: int = 0,
        blinds: List[int] = None,
        action_dicts: List[Dict] = None,
        all_in_runouts: int = 1,
        rake_fraction: float = 0.0,
        max_rake: int = 0
    ):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param starting_stacks: ([[int]])
        :param boards: ([[str]])
        :param ante: (int)
        :param blinds: ([int])
        :param action_dicts: ([dict]) list of dicts like:
            {
                "player": int,
                "action": str,
                "amount": int  [only necessary for bet/call/raises]
            }
        :param all_in_runouts: (int)
        :return: (PokerGameState)
        """
        game_state = cls(
            num_players=num_players,
            deck=deck,
            hands=hands,
            starting_stacks=starting_stacks,
            boards=boards,
            ante=ante,
            blinds=blinds,
            all_in_runouts=all_in_runouts,
            rake_fraction=rake_fraction,
            max_rake=max_rake
        )
        game_state.reset_state_from_action_dicts(action_dicts or [])
        return game_state

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
            f"NotImplementedError in {self.__class__.__name__}: "
            f"You must override get_starting_action "
            f"in subclasses of PokerGameState"
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
            "All PokerGameState objects must implement order_hands "
            "to decide who wins at showdown"
        )

    def get_cards_remaining(self) -> int:
        """
        :return: (int)
        """
        raise NotImplementedError(
            "All PokerGameState objects must implement get_cards_remaining"
        )

    def runout_all_in_board(self, cards_remaining):
        """ append all in runout to board

        :param cards_remaining: (int)
        """
        raise NotImplementedError(
            "All PokerGameState objects must implement runout_all_in_board"
            "to handle multiple runouts after everyone is all-in"
        )

    def reset_all_in_board(self, cards_remaining):
        """ reset board to pre-all-in-runout state

        :param cards_remaining: (int)
        """
        raise NotImplementedError(
            "All PokerGameState objects must implement reset_all_in_board"
            "to handle multiple runouts after everyone is all-in"
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
                f"player {player} only has {self.stacks[player]} chips, "
                f"but trying to put {amount} in pot"
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

    def reset_state_from_action_dicts(self, action_dicts):
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
        self.stacks = [s for s in self.starting_stacks]
        self.pot = Pot(self.num_players, self.rake_fraction, self.max_rake)
        self.last_actions = {}
        self.payouts = {}
        self.extract_antes_and_blinds()
        self.street = 0
        self.action = self.get_starting_action()

        for action_dict in action_dicts:
            self.act(**action_dict)

    def act(self, *args, **kwargs):
        """ create an action, update state and advance the game forward """
        self.append_action(*args, **kwargs)
        self.advance_action()

    def append_action(self, *args, **kwargs):
        """ build and append action to state """
        if self.is_complete:
            raise Exception(
                "cannot append_action after the hand is_complete"
            )
        action_obj = self.build_action(*args, **kwargs)
        self.validate_action(action_obj)
        self.actions.append(action_obj)
        self.update_state_with_action(action_obj)

    def build_action(self, player, action, amount=None, **state):
        """
        :param player: (int)
        :param action: (str)
        :param amount: (int)
        :param state: (dict) extra state to pass into Action
        :return: (Action)
        """
        if amount is None:
            if action == Action.action_call:
                amount = self.amount_to_call
            elif action in Action.zeros:
                amount = 0
            else:
                raise ValueError(
                    f"Amount cannot be None for action type {action}")

        return Action(player=player, action=action, amount=amount, **state)

    def validate_action(self, action):
        """
        :param action: (Action)
        """
        if action.player != self.action:
            raise Exception(
                f"The calculated action is on {self.action}, but "
                f"the next Action object comes from "
                f"{action.player}"
            )

        if action.action not in self.valid_actions:
            raise ValueError(
                f"it is {self.amount_to_call} to call, "
                f"so {action.action} is invalid"
            )

        if self.stacks[action.player] < action.amount:
            # this is prevented by the max_bet property,
            # but added here to make debugging easier
            raise Exception(
                f"Player {action.player} only has "
                f"{self.stacks[action.player]} in stack, "
                f"less than the desired wager of {action.amount}"
            )

        if action.action in Action.aggressions:
            if action.amount < self.min_bet:
                raise ValueError(
                    f"Invalid {action.action} size: "
                    f"amount {action.amount} "
                    f"is less than the minimum of {self.min_bet}"
                )

        if action.action in Action.aggressions:
            if action.amount > self.max_bet:
                raise ValueError(
                    f"Invalid {action.action} size: "
                    f"amount {action.amount} "
                    f"is greater than the limit of {self.max_bet}"
                )

    @property
    def valid_actions(self):
        """
        :return: ({str})
        """
        if self.amount_to_call == 0:
            return Action.zero_to_call
        else:
            return Action.nonzero_to_call

    def update_state_with_action(self, action):
        """
        :param action: (Action)
        :return:
        """
        if action.action in Action.wagers:
            self.put_money_in_pot(player=action.player, amount=action.amount)

        self.last_actions[action.player] = action.action

    def advance_action(self):
        """ move action forward and check if hand is over """
        is_action_closed = self.is_action_closed()

        if not is_action_closed:
            self.move_action()
        else:
            while is_action_closed and self.street < self.showdown_street:
                self.move_street()
                is_action_closed = self.is_action_closed()

        if self.street >= self.showdown_street:
            self.payouts, self.rake_paid = self.get_payouts_and_rake()
            self.is_complete = True

    def get_payouts_and_rake(self):
        """ runout multiple boards if everyone is all in,
            then sort hands and ship Pot

        :return: ({int: int}) player index --> payout
        """
        players_at_showdown = [
            player
            for player in range(self.num_players)
            if self.last_actions.get(player) != Action.action_fold
        ]
        if len(players_at_showdown) < 2:
            return self.pot.settle_showdown(
                winning_players=[players_at_showdown],
                rake_pot=self.should_rake_pot()
            )

        cards_remaining = self.get_cards_remaining()
        num_runouts = (
            self.all_in_runouts
            if cards_remaining and self.action is None
            else 1
        )
        avg_payouts = {p: 0 for p in range(self.num_players)}
        avg_rake = {p: 0 for p in range(self.num_players)}
        for _ in range(num_runouts):
            pot = Pot(
                num_players=self.num_players,
                balances={p: bal for p, bal in self.pot.balances.items()},
                rake_fraction=self.rake_fraction,
                max_rake=self.max_rake
            )
            self.runout_all_in_board(cards_remaining)
            winners = self.order_hands(players_at_showdown)
            runout_payouts, rake_paid = pot.settle_showdown(
                winning_players=winners,
                rake_pot=self.should_rake_pot()
            )
            for p, amt in runout_payouts.items():
                avg_payouts[p] += amt / num_runouts
            for p, amt in rake_paid.items():
                avg_rake[p] += amt / num_runouts
            self.reset_all_in_board(cards_remaining)
        return avg_payouts, avg_rake

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

        if self.is_action_closed():
            self.action = None
            return

        try:
            self.action = self.get_starting_action()
        except StopIteration:
            raise Exception(
                "The action is not closed, but we could not "
                "find the player who starts the action, "
                "so there is a bug. Fix me"
            )

    def is_action_closed(self):
        """ whether the action is closed for a particular street

        :return: (bool)
        """
        return is_action_closed(
            num_players=self.num_players,
            last_actions=self.last_actions,
            pot_balances=self.pot.balances,
            stacks=self.stacks,
        )
    
    def should_rake_pot(self) -> bool:
        raise NotImplementedError(
            'Must implement should_rake_pot in PokerGameState subclasses'
        )

    @property
    def amount_to_call(self):
        """
        :return: (int)
        """
        max_owed_to_pot = (
            max(self.pot.balances.values()) - self.pot.balances[self.action]
        )
        stack_size = self.stacks[self.action]
        return min(stack_size, max_owed_to_pot)

    @property
    def min_bet(self):
        """ in general, the min bet will be the biggest blind
            and the minimum raise will be the difference
            between the last two raises

        :return: (int)
        """
        biggest_blind = max([self.ante, *self.blinds])
        sorted_pot_balances = sorted(self.pot.balances.values(), reverse=True)
        if self.amount_to_call == 0:
            return biggest_blind
        # if amount to call is 0, then this will be zero too
        last_raise_delta = max(
            sorted_pot_balances[0] - sorted_pot_balances[1],
            biggest_blind
        )

        min_bet = last_raise_delta + self.amount_to_call
        stack_size = self.stacks[self.action]
        return min(min_bet, stack_size)

    @property
    def max_bet(self):
        """
        :return: (int)
        """
        return self.stacks[self.action]

    def player_pnl(self, player):
        """
        :param player: (int)
        :return: (float)
        """
        return (
            self.payouts.get(player, 0)
            + self.stacks[player]
            - self.starting_stacks[player]
        )

    @property
    def pnl(self):
        """ map player to their PnL for the hand

        :return: ({int: float})
        """
        return {
            player: self.player_pnl(player)
            for player in range(self.num_players)
        }

    @property
    def state_string(self) -> str:
        """
        :return: (str)
        """
        active_hand = self.hands[self.action]
        return self.build_state_string(
            num_players=self.num_players,
            starting_stacks=self.starting_stacks,
            hand=active_hand,
            boards=self.boards,
            ante=self.ante,
            blinds=self.blinds,
            actions=[a.to_dict() for a in self.actions]
        )

    @property
    def pot_sized_bet(self):
        """
        :return: (int)
        """
        return int(2 * self.amount_to_call + self.pot.total_money)

    @classmethod
    def build_state_string(cls,
                           num_players: int,
                           starting_stacks: List[int],
                           hand: List[str],
                           boards: List[List[str]],
                           ante: int,
                           blinds: List[int],
                           actions: List[Dict]
                           ) -> str:
        """
        :param num_players: (int)
        :param starting_stacks: (List[int])
        :param hand: (List[str])
        :param boards: (List[List[str]])
        :param ante: (int)
        :param blinds: (List[int])
        :param actions: (List[Dict])
        :return: (str)
        """
        boards = [[c for c in board if c] for board in boards]
        return (
            f'{cls.name}{num_players}:'
            f'{"".join(hand)}|'
            f'{",".join("".join(board) for board in boards)}|'
            f'{"".join(cls.transform_action(a) for a in actions)}|'
            f'{ante}-{"/".join(str(b) for b in blinds)}|'
            f'{",".join(str(s) for s in starting_stacks)}'
        )

    @staticmethod
    def transform_action(action: Dict) -> str:
        """
        :param action: (Dict)
            {
                'street': 0,
                'player': 2,
                'action': 'RAISE',
                'amount': 7,
                'pot_sized_bet': 7
            }
        :return: (str)
        """
        if action['action'] not in Action.aggressions:
            return f'{Action.abbreviations[action["action"]]}'
        elif action['amount'] == action.get('pot_sized_bet'):
            return 'p'
        else:
            return f'[{action["amount"]}]'
