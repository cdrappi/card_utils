""" misc utils """


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


def count_in(values, in_set):
    """ get count of values in in_set

    :param values: (str)
    :param in_set: (set(str))
    :return: (int)
    """
    return sum(int(v in in_set) for v in values)
