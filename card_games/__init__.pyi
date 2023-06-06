from __future__ import annotations
import card_games
import typing

__all__ = [
    "get_candidate_melds",
    "get_deadwood",
    "layoff_deadwood",
    "split_melds"
]


def get_candidate_melds(hand: typing.List[str]) -> typing.List[typing.Tuple[int, typing.List[typing.List[str]], typing.List[str]]]:
    """
    Get all candidate melds from list of cards
    """
def get_deadwood(unmelded_cards: typing.List[str]) -> int:
    """
    Get deadwood from list of unmelded cards
    """
def layoff_deadwood(hand: typing.List[str], opp_melds: typing.List[typing.List[str]], stop_on_zero: bool = True) -> typing.Tuple[int, typing.List[typing.List[str]], typing.List[str], typing.List[str]]:
    """
    Layoff deadwood from list of cards
    """
def split_melds(hand: typing.List[str], melds: typing.Optional[typing.List[typing.List[str]]] = None) -> typing.Tuple[int, typing.List[typing.List[str]], typing.List[str]]:
    """
    Split melds from list of cards
    """
