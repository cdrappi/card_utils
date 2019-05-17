""" util functions for omaha games """


def _validate_board(board):
    """ raise exception if board doesn't have exactly 5 cards
    :param board: ([str]) list of 5 cards
    :return:
    """
    if len(board) != 5:
        raise ValueError(
            f'omaha.utils.get_best_hand: '
            f'board must have 5 cards\n'
            f'input: {board}'
        )


def _validate_hands(hands):
    """ raise exception if all hands don't have exactly 4 cards

    :param hands: ([[str]]) list of list of 4 cards
    :return: None
    """
    for hand in hands:
        if len(hand) != 4:
            raise ValueError(
                f'omaha.utils._validate_hands: '
                f'all hands must have 4 cards\n'
                f'hands: {hands}'
            )


def get_best_hand(board, hands):
    """
    :param board: ([str]) list of 5 cards
    :param hands: ([[str]]) list of list of 4 cards
    :return: (int) index of `hands` that makes the strongest omaha hand
    """
    _validate_board(board)
    _validate_hands(hands)

    