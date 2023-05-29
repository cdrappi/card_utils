""" class to store and manipulate the state of a gin ricky game """

import copy
import random
from typing import Dict, List, Optional, Tuple

from card_utils.deck.utils import Card
from card_utils.games.gin.utils import (
    RummyAction,
    RummyEndGame,
    RummyHud,
    RummyTurn,
)


class AbstractGinGameState:
    """store gin ricky game state"""

    deck_dummy_card = "?y"

    def __init__(
        self,
        deck: List[str],
        discard: List[str],
        p1_hand: List[str],
        p2_hand: List[str],
        turn: RummyTurn,
        public_hud: Optional[Dict[str, RummyHud]] = None,
        last_draw=None,
        last_draw_from_discard=None,
        is_complete=False,
        turns=0,
        shuffles=0,
        p1_points=None,
        p2_points=None,
        # defaults are for gin ricky
        cards_dealt: int = 7,
        max_shuffles: Optional[int] = None,
        end_cards_in_deck: int = 0,
        max_turns=None,
        underknock_bonus: int = 0,
        gin_bonus: int = 0,
    ):
        """

        :param deck: ([str])
        :param discard: ([str])
        :param p1_hand: ([str])
        :param p2_hand: ([str])
        :param public_hud: ({str: str})
        :param last_draw: (str)
        :param last_draw_from_discard: (bool)
        :param is_complete: (bool)
        :param turns: (int)
        :param shuffles: (int)
        :param p1_points: (int)
        :param p2_points: (int)
        :param max_shuffles: (int) stop game after this many shuffles
            --> if None, play until someone makes gin
        :param max_turns: (int) stop game after this many turns
            --> if None, play until someone makes gin
        """
        self.deck = deck
        self.discard = discard

        self.p1_hand = p1_hand
        self.p2_hand = p2_hand

        self.turn = turn

        self.last_draw = last_draw
        self.last_draw_from_discard = last_draw_from_discard

        if public_hud is None:
            public_hud = {self.discard[-1]: RummyHud.TOP_OF_DISCARD}
        self.public_hud = public_hud

        self.is_complete = is_complete
        self.turns = turns
        self.shuffles = shuffles

        self.p1_points = p1_points
        self.p2_points = p2_points

        self.cards_dealt = cards_dealt

        self.max_shuffles = max_shuffles
        self.end_cards_in_deck = end_cards_in_deck
        self.max_turns = max_turns
        self.underknock_bonus = underknock_bonus
        self.gin_bonus = gin_bonus

    def draw_card(self, from_discard):
        """draw card from top of deck or discard to player's hand

        :param from_discard: (bool)
        :return: (str) card drawn
        """

        if self.turn not in {RummyTurn.P1_DRAWS, RummyTurn.P2_DRAWS}:
            raise ValueError(
                "Cannot draw: it is not the player's turn to draw"
            )

        if (
            self.turn == RummyTurn.P1_DRAWS
            and len(self.p1_hand) != self.cards_dealt
        ):
            raise Exception(
                f"Player 1 cannot draw because "
                f"they do not have {self.cards_dealt} cards! {self.p1_hand}"
            )
        if (
            self.turn == RummyTurn.P2_DRAWS
            and len(self.p2_hand) != self.cards_dealt
        ):
            raise Exception(
                f"Player 2 cannot draw because "
                f"they do not have {self.cards_dealt} cards! {self.p2_hand}"
            )

        if from_discard:
            card_drawn: str = self.top_of_discard  # type: ignore
            self._add_to_hand(card_drawn)
            self.discard = self.discard[:-1]
            self.public_hud[card_drawn] = (
                RummyHud.PLAYER_1 if self.turn.p1() else RummyHud.PLAYER_2
            )
        else:
            card_drawn = self.top_of_deck
            self._add_to_hand(card_drawn)
            self.deck = self.deck[1:]
            if len(self.deck) == self.end_cards_in_deck:
                self.shuffles += 1
                if self.hit_max_shuffles():
                    self.end_game(RummyEndGame.WALL, 0, 0)
                # if there are no cards left in the deck,
                # shuffle up the discards
                new_deck = copy.deepcopy(self.discard)
                random.shuffle(new_deck)
                self.deck = new_deck
                self.discard = []
                # Both players know each others hands
                # at this point, so we can just do this:
                self.public_hud = {
                    **{c: RummyHud.PLAYER_1 for c in self.p1_hand},
                    **{c: RummyHud.PLAYER_2 for c in self.p2_hand},
                }

        hand = self.p1_hand if self.turn.p1() else self.p2_hand
        deadwood = self.get_deadwood(hand)
        self.turn = self.advance_turn(self.turn, deadwood)
        self.turns += 1
        self.last_draw = card_drawn
        self.last_draw_from_discard = from_discard

        return card_drawn

    @staticmethod
    def get_deadwood(
        hand: List[str],
        melds: Optional[List[List[Card]]] = None,
        opp_melds: Optional[List[List[Card]]] = None,
    ) -> int:
        raise NotImplementedError("get_deadwood not implemented")

    @staticmethod
    def sort_hand(hand: List[str]) -> List[str]:
        raise NotImplementedError("sort_hand not implemented")

    @staticmethod
    def advance_turn(turn: RummyTurn, deadwood: int) -> RummyTurn:
        raise NotImplementedError("advance_turn not implemented")

    def discard_card(self, card) -> None:
        """discard card from player's hand to discard pile

        :param card: (card)
        :return: None
        """

        if self.turn not in {RummyTurn.P1_DISCARDS, RummyTurn.P2_DISCARDS}:
            raise Exception(
                "Cannot discard: it is not the player's turn to discard"
            )

        if self.turn == RummyTurn.P1_DISCARDS:
            if len(self.p1_hand) != self.cards_dealt + 1:
                raise Exception(
                    f"Cannot discard: player 1 has {self.cards_dealt + 1} cards in hand"
                )
            if card not in self.p1_hand:
                raise Exception(
                    f"Player 1 cannot discard {card}: not in hand!"
                )
            self.p1_hand = [c for c in self.p1_hand if c != card]
            hand = self.p1_hand
        elif self.turn == RummyTurn.P2_DISCARDS:
            if len(self.p2_hand) != self.cards_dealt + 1:
                raise Exception(
                    f"Cannot discard: player 2 has {self.cards_dealt + 1} cards in hand"
                )
            if card not in self.p2_hand:
                raise Exception(
                    f"Player 2 cannot discard {card}: not in hand!"
                )
            self.p2_hand = [c for c in self.p2_hand if c != card]
            hand = self.p2_hand
        else:
            raise ValueError("invalid discarding state")

        is_p1 = self.turn.p1()
        deadwood = self.get_deadwood(hand)
        if deadwood == 0:
            opp_hand = self.p2_hand if is_p1 else self.p1_hand
            opp_deadwood = self.get_deadwood(opp_hand)
            p1_deadwood = 0 if is_p1 else opp_deadwood
            p2_deadwood = opp_deadwood if is_p1 else 0
            self.end_game(RummyEndGame.GIN, p1_deadwood, p2_deadwood)
        self.turn = self.advance_turn(self.turn, deadwood)

        # add discard to HUD
        if self.discard:
            self.public_hud[self.discard[-1]] = RummyHud.DISCARD
        self.public_hud[card] = RummyHud.TOP_OF_DISCARD
        self.discard.append(card)

        self.turns += 1
        if self.hit_max_turns():
            self.end_game(RummyEndGame.WALL, 0, 0)

    def decide_knock(
        self,
        knocks: bool,
        melds: Optional[List[List[Card]]] = None,
    ):
        if not self.turn.is_knock():
            raise ValueError(
                "Cannot knock: it is not the player's turn to knock"
            )

        if not knocks:
            self.turn = self.advance_turn(self.turn, 10)  # 10 is arbitrary
            return

        if self.turn == RummyTurn.P1_MAY_KNOCK:
            p1_deadwood = self.get_deadwood(self.p1_hand, melds=melds)
            p2_deadwood = self.get_deadwood(self.p2_hand, opp_melds=melds)
        elif self.turn == RummyTurn.P2_MAY_KNOCK:
            p2_deadwood = self.get_deadwood(self.p2_hand, melds=melds)
            p1_deadwood = self.get_deadwood(self.p1_hand, opp_melds=melds)
        else:
            raise ValueError("invalid knocking state")

        self.end_game(RummyEndGame.KNOCK, p1_deadwood, p2_deadwood)

    def end_game(self, how: RummyEndGame, p1_deadwood: int, p2_deadwood: int):
        """set game state to complete and calculate points for each player"""
        p1 = self.turn.p1()
        self.is_complete = True
        if how == RummyEndGame.WALL:
            self.p1_points = 0
            self.p2_points = 0
        elif how == RummyEndGame.KNOCK:
            self.p1_points = p1_deadwood
            self.p2_points = p2_deadwood
            if p1 and self.p2_points <= self.p1_points:
                self.p2_points += self.underknock_bonus
            elif not p1 and self.p1_points <= self.p2_points:
                self.p1_points += self.underknock_bonus
        elif how == RummyEndGame.GIN:
            self.p1_points = p1_deadwood
            self.p2_points = p2_deadwood
            if p1:
                self.p2_points += self.gin_bonus
            else:
                self.p1_points += self.gin_bonus
        else:
            raise ValueError("invalid end game state")

    def hit_max_shuffles(self):
        """:return: (bool)"""
        if self.max_shuffles is None:
            return False

        return self.shuffles >= self.max_shuffles

    def hit_max_turns(self):
        """:return: (bool)"""
        if self.max_turns is None:
            return False

        return self.turns >= self.max_turns

    def _add_to_hand(self, card_drawn):
        """insert card into player's hand

        :param card_drawn: (str)
        :return: None
        """
        if self.turn == RummyTurn.P1_DRAWS:
            self.p1_hand.append(card_drawn)
        elif self.turn == RummyTurn.P2_DRAWS:
            self.p2_hand.append(card_drawn)
        else:
            raise Exception(
                "Cannot add to hand: it is not the player's turn to draw"
            )

    def get_action(self, is_p1):
        """

        :param is_p1: (bool)
        :return: (str)
        """
        if self.is_complete:
            return RummyAction.COMPLETE

        if is_p1 != self.turn.p1():
            return RummyAction.WAIT

        if self.turn.is_draw():
            return RummyAction.DRAW

        if self.turn.is_discard():
            return RummyAction.DISCARD

        if self.turn.is_knock():
            return RummyAction.KNOCK

    @property
    def top_of_discard(self):
        """
        :return: (str|None)
        """
        if len(self.discard) == 0:
            return None
        return self.discard[-1]

    @property
    def top_of_deck(self):
        """
        :return: (str)
        """
        return self.deck[0]

    def to_dict(self, is_player_1: bool):
        """
        :param is_player_1:
        :return:
        """
        if self.is_complete:
            return self._complete_game_to_dict(is_player_1)
        else:
            return self._incomplete_game_to_dict(is_player_1)

    def _complete_game_to_dict(self, is_player_1: bool):
        """

        :param is_player_1: (bool)
        :return: (dict)
        """
        return {
            "points": self.p1_points if is_player_1 else self.p2_points,
            "opponent_hand": self.p2_hand if is_player_1 else self.p1_hand,
            "opponent_points": (
                self.p2_points if is_player_1 else self.p1_points
            ),
            "action": RummyAction.COMPLETE,
        }

    def _incomplete_game_to_dict(self, is_player_1: bool):
        """

        :param is_player_1: (bool)
        :return: (dict)
        """

        final_info = {
            "action": self.get_action(is_player_1),
            "last_draw": None,
        }
        if final_info["action"] == RummyAction.DRAW.value:
            final_info["last_draw"] = (
                self.last_draw
                if self.last_draw_from_discard
                else self.deck_dummy_card
            )
        if final_info["action"] == RummyAction.DISCARD:
            final_info["drawn_card"] = self.last_draw

        hand = self.sort_hand(self.p1_hand if is_player_1 else self.p2_hand)
        return {
            "hand": hand,
            "points": self.get_deadwood(hand),
            "top_of_discard": self.top_of_discard,
            "last_draw_from_discard": self.last_draw_from_discard,
            "deck_length": len(self.deck),
            "hud": self.player_hud(is_player_1),
            **final_info,
        }

    def player_hud(self, is_player_1: bool):
        """

        :param is_player_1:
        :return:
        """
        hand = self.p1_hand if is_player_1 else self.p2_hand
        return {
            **self._transformed_hud(is_player_1),
            **{c: RummyHud.USER for c in hand},
        }

    def _transformed_hud(self, is_player_1: bool):
        """return the full hud from the player's point of view

        :param is_player_1: (bool)
        :return:
        """
        return {
            card: self._transform_hud_card(loc, is_player_1)
            for card, loc in self.public_hud.items()
        }

    @classmethod
    def _transform_hud_card(cls, card_loc: RummyHud, is_player_1: bool):
        """

        :param card_loc: (str) one of {"1", "2", "t", "d"}
        :param is_player_1: (bool)
        :return: (str) one of {"u", "o", "d", "t"}
        """
        if card_loc == RummyHud.PLAYER_1:
            return RummyHud.USER if is_player_1 else RummyHud.OPPONENT
        elif card_loc == RummyHud.PLAYER_2:
            return RummyHud.USER if not is_player_1 else RummyHud.OPPONENT
        else:
            return card_loc
