import itertools
from enum import Enum
from typing import Dict, Iterable, List, Tuple

from card_utils import deck
from card_utils.deck.utils import (
    Card,
    random_deck,
    rank_partition,
    ranks_to_sorted_values,
)


class RummyAction(Enum):
    DRAW = "draw"
    DISCARD = "discard"
    KNOCK = "knock"
    PASS = "pass"
    COMPLETE = "complete"
    WAIT = "wait"


class RummyTurn(Enum):
    # first draw, where you can pass or not
    P1_DRAWS_FIRST = "p1-draws-first"
    P2_DRAWS_FIRST = "p2-draws-first"

    P1_DRAWS = "p1-draws"
    P2_DRAWS = "p2-draws"

    P1_DISCARDS = "p1-discards"
    P2_DISCARDS = "p2-discards"

    # in rummy, players can opt to knock after discarding
    P1_MAY_KNOCK = "p1-may-knock"
    P2_MAY_KNOCK = "p2-may-knock"

    def p1(self):
        return self in {
            RummyTurn.P1_DRAWS,
            RummyTurn.P1_DRAWS_FIRST,
            RummyTurn.P1_DISCARDS,
            RummyTurn.P1_MAY_KNOCK,
        }

    def is_first_draw(self) -> bool:
        return self in {
            RummyTurn.P1_DRAWS_FIRST,
            RummyTurn.P2_DRAWS_FIRST,
        }

    def is_draw(self):
        return self in {
            RummyTurn.P1_DRAWS,
            RummyTurn.P2_DRAWS,
        }

    def is_discard(self):
        return self in {RummyTurn.P1_DISCARDS, RummyTurn.P2_DISCARDS}

    def is_knock(self):
        return self in {RummyTurn.P1_MAY_KNOCK, RummyTurn.P2_MAY_KNOCK}


class RummyHud(Enum):
    PLAYER_1 = "1"
    PLAYER_2 = "2"
    TOP_OF_DISCARD = "t"
    DISCARD = "d"
    USER = "u"
    OPPONENT = "o"


class RummyEndGame(Enum):
    KNOCK = "knock"
    GIN = "gin"
    WALL = "hit-the-wall"


def new_game(n_cards: int) -> Dict[str, List[Card]]:
    """deal new game of gin

    :param n_cards: (int) how many cards to give to each player
    :return: (dict)
    """
    if 2 * n_cards + 1 >= len(deck.cards):
        raise ValueError(
            f"gin.deal.new_game: too many cards ({n_cards}), "
            f"not enough to deal a game to two players!"
        )

    deck_ = random_deck()
    return {
        "p1_hand": deck_[0:n_cards],
        "p2_hand": deck_[n_cards : 2 * n_cards],
        "discard": [deck_[2 * n_cards]],
        "deck": deck_[2 * n_cards + 1 :],
    }


def get_sets(hand: List[str]) -> Tuple[List[List[Card]], List[List[Card]]]:
    """

    :param hand: ([str])
    :return: ([[str]], [[str]])
    """
    rank_to_suits = rank_partition(hand)
    sets_3, sets_4 = [], []
    for rank, suits in rank_to_suits.items():
        if len(suits) == 4:
            sets_4.append([f"{rank}{s}" for s in suits])
            sets_3.extend(
                [
                    [f"{rank}{s}" for s in suit_combo]
                    for suit_combo in itertools.combinations(suits, 3)
                ]
            )
        elif len(suits) == 3:
            sets_3.append([f"{rank}{s}" for s in suits])
    return sets_3, sets_4


def rank_straights(
    ranks: List[str],
    min_len: int = 3,
    max_len: int = 13,
    aces_high=True,
    aces_low=True,
    suit="",
) -> List[List[str]]:
    """
    :param ranks: ([str])
        e.g. ['A', '2', '7', 'T', 'J', 'Q', 'K']
    :param straight_length: (int) e.g. 5
    :param aces_high: (bool)
    :param aces_low: (bool)
    :param suit: (str) optional: inject a suit in the final returned value
    :return: ([[str]]) list of list of straights,
        each with length straight_length
        e.g. [['T','J','Q','K','A']]
        or [['Th', 'Jh', 'Qh', 'Kh', 'Ah']]
    """
    if len(ranks) < min_len:
        # don't waste our time if its impossible to make a straight
        return []

    if suit not in {"", *deck.suits}:
        raise ValueError(
            f"rank_straights: suit parameter must either be "
            f'the empty string "" or one of {deck.suits}'
        )

    values = ranks_to_sorted_values(
        ranks,
        aces_high=aces_high,
        aces_low=aces_low,
    )

    values_in_a_row = 0
    num_values = len(values)
    last_value = values[0]
    straights = []

    for ii, value in enumerate(values[1:]):
        if last_value + 1 == value:
            values_in_a_row += 1
        else:
            values_in_a_row = 0

        for straight_length in range(min_len, max_len + 1):
            if values_in_a_row >= straight_length - 1:
                straights.append(
                    [
                        f"{deck.value_to_rank[v]}{suit}"
                        for v in range(value - straight_length + 1, value + 1)
                    ]
                )

        if num_values + values_in_a_row < min_len + ii:
            # exit early if there aren't enough cards left
            # to complete a straight
            return straights

        last_value = value

    return straights


def sort_cards_by_rank(cards: Iterable[str]):
    """
    :param cards: ([str])
    :return: ([str])
    """
    return sorted(cards, key=lambda c: deck.rank_to_value[c[0]])
