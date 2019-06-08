from card_utils.deck.utils import random_deck
from card_utils.games.poker import inverse_hand_order


def pretty_hand_rank(hand_rank_tuple):
    """
    :param hand_rank_tuple: (tuple(int))
    :return: (str)
    """
    hand_order_ = next(hand_rank_tuple)
    return inverse_hand_order[hand_order_]


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
