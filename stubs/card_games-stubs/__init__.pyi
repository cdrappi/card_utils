from __future__ import annotations
import card_games
import typing

__all__ = [
    "add",
    "get_candidate_melds",
    "get_deadwood",
    "split_melds"
]


def add(arg0: int, arg1: int) -> int:
    """
    A function which adds two numbers
    """
def get_candidate_melds(arg0: typing.List[str]) -> typing.List[typing.Tuple[int, typing.List[typing.List[str]], typing.List[str]]]:
    """
    Get all candidate melds from list of cards
    """
def get_deadwood(arg0: typing.List[str]) -> int:
    """
    Get deadwood from list of unmelded cards
    """
def split_melds(hand: typing.List[str], melds: typing.Optional[typing.List[typing.List[str]]] = None) -> typing.Tuple[int, typing.List[typing.List[str]], typing.List[str]]:
    """
    Split melds from list of cards
    """
