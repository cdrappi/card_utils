""" class to store and manipulate the state of a gin ricky game """

import copy
import random

from gin_utils.ricky import utils


class GinRickyGameState:
    """ store gin ricky game state """

    hud_player_1 = "1"
    hud_player_2 = "2"
    hud_top_of_discard = "t"
    hud_discard = "d"
    hud_user = "u"
    hud_opponent = "o"

    deck_dummy_card = "?y"

    action_draw = 'draw'
    action_discard = 'discard'
    action_complete = 'complete'
    action_wait = 'wait'

    def __init__(self,
                 deck, discard,
                 p1_hand, p2_hand,
                 p1_discards, p1_draws, p2_discards, p2_draws,
                 public_hud=None, last_draw=None, last_draw_from_discard=None,
                 is_complete=False, turns=0, shuffles=0,
                 p1_points=None, p2_points=None,
                 max_turns=None, max_shuffles=None):
        """

        :param deck: ([str])
        :param discard: ([str])
        :param p1_hand: ([str])
        :param p2_hand: ([str])
        :param p1_discards: (bool)
        :param p1_draws: (bool)
        :param p2_discards: (bool)
        :param p2_draws: (bool)
        :param public_hud: ({str: str})
        :param last_draw: (str)
        :param last_draw_from_discard: (bool)
        :param is_complete: (bool)
        :param turns: (int)
        :param shuffles: (int)
        :param p1_points: (int)
        :param p2_points: (int)
        """
        self.deck = deck
        self.discard = discard

        self.p1_hand = p1_hand
        self.p2_hand = p2_hand

        self.p1_discards = p1_discards
        self.p1_draws = p1_draws
        self.p2_discards = p2_discards
        self.p2_draws = p2_draws

        self.last_draw = last_draw
        self.last_draw_from_discard = last_draw_from_discard

        if public_hud is None:
            public_hud = {self.discard[-1]: self.hud_top_of_discard}
        self.public_hud = public_hud

        self.is_complete = is_complete
        self.turns = turns
        self.shuffles = shuffles

        self.p1_points = p1_points
        self.p2_points = p2_points

        self.max_turns = max_turns
        self.max_shuffles = max_shuffles

    def draw_card(self, from_discard):
        """ draw card from top of deck or discard to player's hand

        :param from_discard: (bool)
        :return: (str) card drawn
        """

        if self.p1_draws == self.p2_draws:
            raise Exception(
                'exactly one player must be drawing '
                'to call GinRickyGameState.draw_card'
            )

        if self.p1_draws and len(self.p1_hand) != 7:
            raise Exception(
                f'Player 1 cannot draw because '
                f'they do not have 7 cards! {self.p1_hand}'
            )
        if self.p2_draws and len(self.p2_hand) != 7:
            raise Exception(
                f'Player 2 cannot draw because '
                f'they do not have 7 cards! {self.p2_hand}'
            )

        if from_discard:
            card_drawn = self.top_of_discard
            self._add_to_hand(card_drawn)
            self.discard = self.discard[:-1]
            self.public_hud[card_drawn] = (
                self.hud_player_1 if self.p1_draws
                else self.hud_player_2
            )
        else:
            card_drawn = self.top_of_deck
            self._add_to_hand(card_drawn)
            self.deck = self.deck[1:]
            if len(self.deck) == 0:
                # if there are no cards left in the deck,
                # shuffle up the discards
                new_deck = copy.deepcopy(self.discard)
                random.shuffle(new_deck)
                self.deck = new_deck
                self.discard = []
                self.shuffles += 1
                # Both players know each others hands
                # at this point, so we can just do this:
                self.public_hud = {
                    **{c: self.hud_player_1 for c in self.p1_hand},
                    **{c: self.hud_player_2 for c in self.p2_hand}
                }
                if self.exceeded_max_shuffles():
                    self.end_game()

        if self.p1_draws:
            self.p1_draws = False
            self.p1_discards = True
        elif self.p2_draws:
            self.p2_draws = False
            self.p2_discards = True

        self.turns += 1
        self.last_draw = card_drawn
        self.last_draw_from_discard = from_discard

        return card_drawn

    def discard_card(self, card):
        """ discard card from player's hand to discard pile

        :param card: (card)
        :return: None
        """

        if self.p1_discards == self.p2_discards:
            raise Exception(
                'exactly one player must be discarding '
                'to call GinRickyGameState.discard_card'
            )

        if self.p1_discards:
            if len(self.p1_hand) != 8:
                raise Exception(f'Cannot discard: player 1 has 8 cards in hand')
            if card not in self.p1_hand:
                raise Exception(f'Player 1 cannot discard {card}: not in hand!')
            self.p1_hand = [c for c in self.p1_hand if c != card]
            self.p1_discards = False
            self.p2_draws = True
            if utils.hand_points(self.p1_hand) == 0:
                self.end_game()
        elif self.p2_discards:
            if len(self.p2_hand) != 8:
                raise Exception(f'Cannot discard: player 2 has 8 cards in hand')
            if card not in self.p2_hand:
                raise Exception(f'Player 2 cannot discard {card}: not in hand!')
            self.p2_hand = [c for c in self.p2_hand if c != card]
            self.p2_discards = False
            self.p1_draws = True
            if utils.hand_points(self.p2_hand) == 0:
                self.end_game()

        # add discard to HUD
        if self.discard:
            self.public_hud[self.discard[-1]] = self.hud_discard
        self.public_hud[card] = self.hud_top_of_discard
        self.discard.append(card)

        self.turns += 1
        if self.exceeded_max_turns():
            self.end_game()

    def end_game(self):
        self.is_complete = True
        self.p1_points = utils.hand_points(self.p1_hand)
        self.p2_points = utils.hand_points(self.p2_hand)

    def exceeded_max_shuffles(self):
        if self.max_shuffles is None:
            return False

        return self.shuffles > self.max_shuffles

    def exceeded_max_turns(self):
        if self.max_turns is None:
            return False

        return self.turns > self.max_turns

    def _add_to_hand(self, card_drawn):
        """ insert card into player's hand

        :param card_drawn: (str)
        :return: None
        """
        if self.p1_draws:
            self.p1_hand.append(card_drawn)
        else:
            self.p2_hand.append(card_drawn)

    def get_action(self, is_p1):
        """

        :param is_p1: (bool)
        :return: (str)
        """

        if self.is_complete:
            return self.action_complete

        is_p2 = not is_p1
        if (self.p1_draws and is_p1) or (self.p2_draws and is_p2):
            return self.action_draw
        elif (is_p1 and self.p1_discards) or (is_p2 and self.p2_discards):
            return self.action_discard
        else:
            return self.action_wait

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

    def to_dict(self, is_player_1):
        """
        :param is_player_1:
        :return:
        """
        if self.is_complete:
            return self._complete_game_to_dict(is_player_1)
        else:
            return self._incomplete_game_to_dict(is_player_1)

    def _complete_game_to_dict(self, is_player_1):
        """

        :param is_player_1: (bool)
        :return: (dict)
        """
        return {
            'points': self.p1_points if is_player_1 else self.p2_points,
            'opponent_hand': self.p2_hand if is_player_1 else self.p1_hand,
            'opponent_points': self.p2_points if is_player_1 else self.p1_points,
            'action': self.action_complete,
        }

    def _incomplete_game_to_dict(self, is_player_1):
        """

        :param is_player_1: (bool)
        :return: (dict)
        """

        final_info = {
            'action': self.get_action(is_player_1),
            'last_draw': None
        }
        if final_info['action'] == self.action_draw:
            final_info['last_draw'] = (
                self.last_draw
                if self.last_draw_from_discard
                else self.deck_dummy_card
            )
        if final_info['action'] == self.action_discard:
            final_info['drawn_card'] = self.last_draw

        hand = utils.sort_hand(self.p1_hand if is_player_1 else self.p2_hand)
        return {
            'hand': hand,
            'points': utils.hand_points(hand),
            'top_of_discard': self.top_of_discard,
            'deck_length': len(self.deck),
            'hud': self.player_hud(is_player_1),
            **final_info,
        }

    def player_hud(self, is_player_1):
        """

        :param is_player_1:
        :return:
        """
        hand = self.p1_hand if is_player_1 else self.p2_hand
        return {
            **self._transformed_hud(is_player_1),
            **{c: self.hud_user for c in hand}
        }

    def _transformed_hud(self, is_player_1):
        """ return the full hud from the player's point of view

        :param is_player_1: (bool)
        :return:
        """
        return {
            card: self._transform_hud_card(loc, is_player_1)
            for card, loc in self.public_hud.items()
        }

    @classmethod
    def _transform_hud_card(cls, card_loc, is_player_1):
        """

        :param card_loc: (str) one of {"1", "2", "t", "d"}
        :param is_player_1: (bool)
        :return: (str) one of {"u", "o", "d", "t"}
        """
        if card_loc == cls.hud_player_1:
            return cls.hud_user if is_player_1 else cls.hud_opponent
        elif card_loc == cls.hud_player_2:
            return cls.hud_user if not is_player_1 else cls.hud_opponent
        else:
            return card_loc
