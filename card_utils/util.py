""" misc utils """

from typing import List, Union


def untuple_dict(the_dict):
    """convert dict with keys that are tuples
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


def inverse_cumulative_sum(increasing_numbers: List[int]):
    """inverse function of cumulative sum

    :param increasing_numbers: ([number]) [1,3,6]
    :return: ([number]) [1,2,3]
    """
    if not increasing_numbers:
        return []

    inv_cumsum = [increasing_numbers[0]]
    for e1, e2 in zip(increasing_numbers[:-1], increasing_numbers[1:]):
        inv_cumsum.append(e2 - e1)

    return inv_cumsum


class LightDefaultDict(dict):
    def __init__(self, default_factory, **kwargs):
        """
        :param default_factory: (function) e.g. int, float, list
        """
        dict.__init__(self, **kwargs)
        self.default_factory = default_factory

    def __getitem__(self, item):
        """
        :param item: (hashable object)
        :return: (object)
        """
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            return self.default_factory()


def count_items(items):
    """
    :param items: (list)
    :return: (dict) items --> count of item
    """
    counts = LightDefaultDict(int)

    for item in items:
        counts[item] += 1

    return counts
