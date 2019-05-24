""" misc utils """

from typing import List, Union


def untuple_dict(the_dict):
    """ convert dict with keys that are tuples
        to a dict with keys that are strings

    :param the_dict: ({tuple: obj})
    :return: ({str: obj})
    """

    def to_key(obj):
        return (
            f'({",".join(str(o) for o in obj)})'
            if isinstance(obj, tuple)
            else obj
        )

    return {to_key(k): v for k, v in the_dict.items()}


def inverse_cumulative_sum(increasing_numbers: List[Union[int, float]]):
    """ inverse function of cumulative sum

    :param increasing_numbers: ([number]) [1,3,6]
    :return: ([number]) [1,2,3]
    """
    if not increasing_numbers:
        return []

    inv_cumsum = [increasing_numbers[0]]
    for e1, e2 in zip(increasing_numbers[:-1], increasing_numbers[1:]):
        inv_cumsum.append(e2 - e1)

    return inv_cumsum
