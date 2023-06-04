import typing

__all__ = ["get_candidate_melds", "get_deadwood", "split_melds"]

def get_candidate_melds(
    hand: typing.List[str],
) -> typing.List[
    typing.Tuple[int, typing.List[typing.List[str]], typing.List[str]]
]:
    """
    Get all candidate melds from list of cards
    """

def get_deadwood(unmelded_cards: typing.List[str]) -> int:
    """
    Get deadwood from list of unmelded cards
    """

def split_melds(
    hand: typing.List[str],
    melds: typing.Optional[typing.List[typing.List[str]]] = None,
) -> typing.Tuple[int, typing.List[typing.List[str]], typing.List[str]]:
    """
    Split melds from list of cards
    """
