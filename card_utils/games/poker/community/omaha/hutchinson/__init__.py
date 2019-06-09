"""
http://erh.homestead.com/omaha.html
"""
from card_utils.deck.utils import (
    rank_partition,
    suit_partition,
    ranks_to_sorted_values,
)

flush_contribution_values = {
    'A': 8,
    'K': 6,
    'Q': 5,
    'J': 4,
    'T': 3,
    '9': 3,
    '8': 2,
    **{str(r): 1 for r in range(2, 8)}
}

pair_contribution_values = {
    'A': 18,
    'K': 16,
    'Q': 14,
    'J': 13,
    'T': 12,
    '9': 10,
    '8': 8,
    **{str(r): 7 for r in range(2, 8)}
}

straight_contribution_values = {
    4: 25,
    3: 18,
    2: 8
}


def hi_point_count(hand):
    """
    :param hand: ([str]) 4 cards
    :return: (int)
    """
    return (
        flushes_contribution(hand)
        + pairs_contribution(hand)
        + straights_contribution(hand)
    )


def flushes_contribution(hand):
    """
    :param hand: ([str])
    :return: (int)

    FIRST,
    to evaluate the contribution made by suited cards,
    look to see if your hand contains two or more cards
    of the same suit. If it does, award points based upon
    the rank of the highest card. Repeat the procedure
    if your hand is double suited.

    If the highest card is an ACE award 8 points
    If the highest card is a KING award 6 points
    If the highest card is a QUEEN award 5 points
    If the highest card is a JACK award 4 points
    If the highest card is a TEN or a NINE award 3 points
    If the highest card is an EIGHT award 2 points
    If the highest card is SEVEN or below award 1 point.

    If your hand contains more than two cards of the same suit, deduct 2 points.
    """
    return sum(
        max(flush_contribution_values[r] for r in ranks)
        for suit, ranks in suit_partition(hand).items()
        if len(ranks) >= 2
    )


def pairs_contribution(hand):
    """
    :param hand: ([str])
    :return: (int)

    SECOND, to factor in the advantage of having pairs,

    If you have a pair of ACES award 18 points
    If you have a pair of KINGS award 16 points
    If you have a pair of QUEENS award 14 points
    If you have a pair of JACKS award 13 points
    If you have a pair of TENS award 12 points
    If you have a pair of NINES award 10 points
    If you have a pair of EIGHTS award 8 points
    If you have a pair of SEVENS or below award 7 points

    Award no points to any hand that contains three of the same rank.
    """
    return sum(
        pair_contribution_values[rank]
        for rank, suits in rank_partition(hand).items()
        # NOTE: if we have 3 of a kind, we get a 0 also
        if len(suits) == 2
    )


def straights_contribution(hand):
    """
    :param hand: ([str])
    :return: (int)

    THIRD,
    when your hand contains cards capable
    of completing a straight it becomes more valuable.
    Therefore, If your cards contain no more than
    a three card gap, add the following points:

        For FOUR cards, add 25 points
        For THREE cards, add 18 points
        For TWO cards, add 8 points

    From these totals, subtract two points for each gap,
    up to a maximum of six points.

    To account for the special case represented by ACES,
    deduct four points from the above totals when an Ace is used.
    This is necessary because an Ace can make fewer straights.
    However, when your hand contains small cards that can be
    used with an Ace to make a straight, the hand's value increases.
    Therefore, when your hand contains an Ace and another wheel card,
    add 6 points. Add 12 points for an Ace and two wheel cards.
    """
    sorted_values = ranks_to_sorted_values(
        ranks=[r for r, _ in hand],
        aces_high=True,
        aces_low=True,
        distinct=True
    )

    four_contribution, _ = _straights_contribution(sorted_values, 4)
    if four_contribution:
        return four_contribution

    three_contribution, indices = _straights_contribution(sorted_values, 3)
    if three_contribution:
        # check if there is also a dangling two contribution
        assert len(indices) == 1
        [[i1, i2, i3]] = indices
        if i1 > 0:
            low_two_contribution, _ = _straights_contribution(sorted_values[:i2], 2)
            three_contribution += low_two_contribution
        if i3 < 4:
            high_two_contribution, _ = _straights_contribution(sorted_values[i3:], 2)
            three_contribution += high_two_contribution
        return three_contribution

    two_contribution, _ = _straights_contribution(sorted_values, 2)
    return two_contribution


def _straights_contribution(sorted_values, subset_size):
    """
    :param sorted_values: ([int])
    :param subset_size: (int) 2, 3 or 4
    :return: (int, [[int]])
    """
    n_values = len(sorted_values)
    contributing_indices = []

    count = 0
    for ii in range(n_values + 1 - subset_size):
        sub_contribution = _straights_sub_contribution(
            sorted_values_sublist=sorted_values[ii:ii + subset_size]
        )
        if sub_contribution:
            count += sub_contribution
            contributing_indices.append(list(range(ii, ii + subset_size)))

    return count, contributing_indices


def _straights_sub_contribution(sorted_values_sublist):
    """
    :param sorted_values_sublist: ([int])
    :return: (int)
    """
    count = 0

    n_values = len(sorted_values_sublist)
    n_gaps = (
        max(sorted_values_sublist)
        - min(sorted_values_sublist)
        - n_values
        + 1
    )
    if n_gaps <= 3:
        count += straight_contribution_values[n_values] - 2 * n_gaps

        has_hi_ace = 14 in sorted_values_sublist
        has_lo_ace = 1 in sorted_values_sublist
        if has_lo_ace or has_hi_ace:
            count -= 4

    return count
