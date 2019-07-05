from typing import Dict, List

from card_utils.deck.utils import random_deck
from card_utils.games.poker import inverse_hand_order
from card_utils.games.poker.action import Action
from card_utils.games.poker.pot import Pot


def pretty_hand_rank(hand_rank_tuple):
    """
    :param hand_rank_tuple: (tuple(int))
    :return: (str)
    """
    return inverse_hand_order[hand_rank_tuple[0]]


def get_best_hands_generic(hand_strength_function, board, hands):
    """ get the index of the best omaha hand given a board

    :param hand_strength_function: (function)
        inputs (board, hand), outputs (tuple)
    :param board: ([str]) list of 5 cards
    :param hands: ([set(str)]) list of sets of 4 cards
    :return: ([[int]]) indices of `hands` that makes the strongest omaha hand
        --> this is a list of lists because it is possible to "chop" with
            every hand rank except straight flushes, quads and flushes
    """
    hand_strengths = {}
    for ii, hand in enumerate(hands):
        hand_strength = hand_strength_function(board, hand)
        if hand_strength not in hand_strengths:
            hand_strengths[hand_strength] = []
        hand_strengths[hand_strength].append(ii)

    return [
        hand_strengths[hs]
        for hs in sorted(hand_strengths, reverse=True)
    ]


def deal_random_hands(n_hands, n_cards):
    """ deal random n_hands of n_cards each,
        and also return the rest of the deck

    :param n_hands: (int)
    :param n_cards: (int)
    :return: ([str], [[str]]) remaining deck, hands
    """
    deck = random_deck()
    hands = [
        deck[n_cards * ii:n_cards * (ii + 1)]
        for ii in range(n_hands)
    ]
    return deck[n_cards * n_hands:], hands


def is_action_closed(num_players: int, last_actions: Dict, pot: Pot, stacks: List[int]) -> bool:
    """
    :param num_players: (int)
    :param last_actions: (Dict)
    :param pot: (Pot)
    :param stacks: (List[int])
    :return: (bool)
    """
    folders = 0
    checkers = 0
    all_in_last_street = 0
    not_yet_acted = 0
    not_all_in_set = set()

    for player in range(num_players):
        last_action = last_actions.get(player)
        is_all_in = stacks[player] == 0

        if last_action != Action.action_fold and not is_all_in:
            not_all_in_set.add(player)

        if last_action is None and is_all_in:
            all_in_last_street += 1
        elif last_action is None:
            not_yet_acted += 1
        elif last_action == Action.action_fold:
            folders += 1
        elif last_action == Action.action_check:
            checkers += 1

    not_all_in_balances = {
        *{pot.balances[p] for p in not_all_in_set},
        max(pot.balances.values()),
    }
    if len(not_all_in_balances) > 1:
        # if those who are not all in but have not folded
        # have different balances, and their balance is not equal
        # to the max any player has put in the pot,
        # then we action is not complete
        return False

    if folders == num_players - 1:
        # Case 1: everyone folds except 1 person
        return True

    if len(not_all_in_balances) == 1:
        # Case 2: if everyone is all in except one person,
        # then everyone else must have either
        # folded or been all in last street
        if folders + all_in_last_street == num_players - 1:
            return True

    if folders + checkers + all_in_last_street == num_players:
        # Case 3: no one this street has made any bets,
        # and everyone had either folded or went all on a previous street,
        # or checked on this street
        return True

    # Case 4:
    # Everyone must have acted and not checked
    return not_yet_acted == 0
