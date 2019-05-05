import itertools

from deal import new_game
from deck import card_values


def deal_new_game():
    """ shuffle up and deal each player 7 cards,
        put one card in the discard list,
        and put remaining cards in deck

    :return: (dict)
        {
            'p1_hand': [str],
            'p2_hand': [str],
            'discard': [str],
            'deck':    [str]
        }
    """
    return new_game(cards=7)


def hand_points(hand):
    """

    :param hand: ([str]) list of cards
    :return: (int)
    """
    points = 14 * 7
    for combo_3, combo_4, *_ in yield_hand_combos(hand):
        combo_points_ = combos_points(combo_3, combo_4)
        if combo_points_ == 0:
            return 0
        points = min(combo_points_, points)

    return points


def yield_hand_combos(hand):
    """

    :param hand: ([str]) either 7 or 8 cards
    :return:
    """
    for combo_3 in itertools.combinations(hand, 3):
        remaining_cards = [c for c in hand if c not in combo_3]
        if len(remaining_cards) == 5:
            # not using itertools.combinations(remaining_cards, 1) here,
            # because it returns a tuple with 1 item rather than sole item
            for left_out_card in remaining_cards:
                combo_4 = [c for c in remaining_cards if c != left_out_card]
                yield combo_3, combo_4, left_out_card
        elif len(remaining_cards) == 4:
            yield combo_3, remaining_cards
        else:
            raise Exception(f"incorrect number of cards ({len(hand)}) in hand")


def combos_points(combo_3, combo_4):
    """

    :param combo_3: ([str]) 3 cards
    :param combo_4: ([str]) 4 cards
    :return:
    """
    return combo_points(combo_3) + combo_points(combo_4)


def combo_points(card_combo):
    """

    :param card_combo: ([str])
    :return: (int)
    """
    first_rank, first_suit = card_combo[0]
    card_ranks = [card[0] for card in card_combo]

    if all(r == first_rank for r in card_ranks):
        # all cards are same rank
        return 0

    if any(card[1] != first_suit for card in card_combo):
        # cards are not of same rank and not of same suit,
        # so return the points
        return sum_card_ranks(card_ranks)

    # NOTE: if we get to this point, cards have same suit
    # so we just need to check if they make a valid 3- or 4-straight

    # handle fact that aces can be 1 or 14
    values_ace_as_1 = sorted(card_values[r] for r in card_ranks)
    rank_combos = [values_ace_as_1]
    if any(r == 'A' for r in card_ranks):
        rank_combos.append(sorted(14 if value == 1 else value for value in values_ace_as_1))

    for rank_combo in rank_combos:
        if ranks_make_a_straight(rank_combo):
            return 0

    return sum_card_ranks(card_ranks)


def sum_card_ranks(card_ranks):
    """

    :param card_ranks: (str) e.g. "Q" or "2"
    :return:
    """
    return sum(card_values[r] for r in card_ranks)


def ranks_make_a_straight(rank_combo):
    """

    :param rank_combo: ([int])
    :return: (bool)
    """
    for r1, r2 in zip(rank_combo[:-1], rank_combo[1:]):
        if r1 != r2 - 1:
            return False
    return True
