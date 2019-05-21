import collections

from card_utils.deck.utils import (
    ranks_to_sorted_values,
)
from card_utils.games.poker import (
    hand_order,
    STRAIGHT_FLUSH,
    QUADS,
    FULL_HOUSE,
    FLUSH,
    STRAIGHT,
    THREE_OF_A_KIND,
    TWO_PAIR,
    ONE_PAIR,
    HIGH_CARD,
)


def five_card_hand_rank(five_card_hand):
    """

    :param five_card_hand: ([str]) a hand of exactly 5 cards
    :return:
    """
    if len(five_card_hand) != 5:
        raise ValueError(
            f'input to five_card_hand_rank must be a list of 5 cards'
        )

    is_flush = len(set(suit for _, suit in five_card_hand)) == 1

    sorted_values = ranks_to_sorted_values(
        ranks=[rank for rank, _ in five_card_hand],
        aces_low=True,
        aces_high=True
    )
    sorted_distinct_values = sorted(set(sorted_values))
    straight_value = _best_straight_from_sorted_distinct_values(sorted_distinct_values)
    if is_flush and straight_value:
        return hand_order[STRAIGHT_FLUSH], straight_value

    ah_sorted_values = ranks_to_sorted_values(
        ranks=[rank for rank, _ in five_card_hand],
        aces_low=False,
        aces_high=True,
        reverse=True
    )
    inverse_ah_value_counts = _get_inverse_ah_value_counts(ah_sorted_values)
    if inverse_ah_value_counts[4] and inverse_ah_value_counts[1]:
        # four-of-a-kind!
        quads_value, *_ = inverse_ah_value_counts[4]
        kicker_value, *_ = inverse_ah_value_counts[1]
        return hand_order[QUADS], quads_value, kicker_value

    if inverse_ah_value_counts[3] and inverse_ah_value_counts[2]:
        # full house!
        trips_value, *_ = inverse_ah_value_counts[3]
        pair_value, *_ = inverse_ah_value_counts[2]
        return hand_order[FULL_HOUSE], trips_value, pair_value

    if is_flush:
        return (hand_order[FLUSH], *inverse_ah_value_counts[1])

    if straight_value:
        return hand_order[STRAIGHT], straight_value

    if inverse_ah_value_counts[3]:
        trips_value, *_ = inverse_ah_value_counts[3]
        kicker_1, kicker_2 = inverse_ah_value_counts[1]
        if kicker_1 <= kicker_2:
            raise ValueError(
                f'Kicker 1 cannot be <= Kicker 2! '
                f'There is either a sorting error (<) '
                f'or we missed a full house (=)'
            )
        return hand_order[THREE_OF_A_KIND], trips_value, kicker_1, kicker_2

    num_pairs = len(inverse_ah_value_counts[2])
    num_singletons = len(inverse_ah_value_counts[1])
    if num_pairs == 2 and num_singletons == 1:
        # two pair
        top_pair, bottom_pair = inverse_ah_value_counts[2]
        kicker, *_ = inverse_ah_value_counts[1]
        return hand_order[TWO_PAIR], top_pair, bottom_pair, kicker

    if num_pairs == 1 and num_singletons == 3:
        # one pair
        pair, *_ = inverse_ah_value_counts[2]
        kicker_1, kicker_2, kicker_3 = inverse_ah_value_counts[1]
        return hand_order[ONE_PAIR], pair, kicker_1, kicker_2, kicker_3

    if num_singletons != 5:
        raise ValueError(
            f'ValueError in five_card_hand_rank! '
            f'No straight, flush or pairs+, '
            f'but we do not have 5 distinct cards. '
            f'Instead we have {five_card_hand}'
        )

    return (hand_order[HIGH_CARD], *inverse_ah_value_counts[1])


def _best_straight_from_sorted_distinct_values(sorted_distinct_values):
    """
    :param sorted_distinct_values: ([int])
    :return: (int) best straight or 0 if none
    """
    if len(set(sorted_distinct_values)) != len(sorted_distinct_values):
        raise Exception(
            f'Input to _best_straight_from_sorted_distinct_values '
            f'must be a sorted list of distinct values'
        )

    if len(sorted_distinct_values) == 5:
        max_value = max(sorted_distinct_values)
        is_straight = (
            # we make a straight if there are 5 distinct values
            len(sorted_distinct_values) == 5 and
            # and the top value minus the bottom value is equal to 4
            max_value - min(sorted_distinct_values) == 4
        )
        return max_value if is_straight else 0
    elif len(sorted_distinct_values) == 6:
        return max(
            # recursively call for ace-low straights
            _best_straight_from_sorted_distinct_values(sorted_distinct_values[:-1]),
            # recursively call for ace-high straights
            _best_straight_from_sorted_distinct_values(sorted_distinct_values[1:])
        )

    # otherwise, there's no straight
    return 0


def _get_inverse_ah_value_counts(aces_high_values):
    """
    :param aces_high_values: ([str]) e.g. [2, 12, 13, 14, 14]
    :return: ({int: [int]}) e.g. {2: [14], 1: [13,12,2]}
    """
    ah_value_counts = collections.Counter(aces_high_values)

    reverse_counts = collections.defaultdict(list)
    for value, ct in ah_value_counts.items():
        reverse_counts[ct].append(value)

    for ct in reverse_counts:
        reverse_counts[ct].sort(reverse=True)

    return reverse_counts
