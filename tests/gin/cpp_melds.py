from typing import List, Optional
from typing import Tuple
from card_utils.deck.utils import Card
from card_utils.games.gin.rummy.utils import deal_new_game, split_melds
import card_games
import time

from card_utils.games.gin.rummy.game_state import GinRummyGameState


def _test_hand(hand: List[Card]) -> Tuple[float, float]:
    # print("------")
    # print(hand)
    # print(GinRummyGameState.sort_hand(hand))

    start_cpp = time.time()
    cpp_dw, cpp_melds, cpp_um = card_games.split_melds(hand, None)
    end_cpp = time.time()
    py_dw, py_melds, py_um = split_melds(hand)
    start_py = time.time()
    if cpp_dw != py_dw:
        print(f"deadwoods do not match: {cpp_dw=}, {py_dw=}")
        print(f"cpp unmelded: {cpp_um}")
        print(f"py unmelded: {py_um}")
        raise ValueError("cpp_dw != py_dw")
    return (end_cpp - start_cpp, start_py - end_cpp)


def _test_deadwood(min_deadwood: Optional[int] = None) -> Tuple[float, float]:
    new_game = deal_new_game()
    hand = new_game["p1_hand"]
    if min_deadwood is not None:
        dw = GinRummyGameState.get_deadwood(hand)
        if dw >= min_deadwood:
            return 0.0, 0.0
    return _test_hand(hand)


def _test_layoffs() -> None:
    hand = ["5c", "5d", "5h", "3s", "4s", "5s", "Ac", "Ad", "4h", "7s"]
    opp_melds = [["3h", "3d", "3c"], ["7c", "7d", "7h"]]
    dw, *_ = card_games.layoff_deadwood(hand, opp_melds, True)
    assert dw == 6, f"{dw=}"

    hand = ["5c", "5d", "5h", "9d", "Td", "Jd", "3s", "4s", "Ac", "Ad"]
    opp_melds = [["5s", "6s", "7s"], ["7c", "7d", "7h"]]
    dw, *_ = card_games.layoff_deadwood(hand, opp_melds, True)
    assert dw == 2

    hand = ["5c", "5d", "5h", "9d", "Td", "Jd", "3s", "4s", "Ac", "Ad"]
    opp_melds = [["5s", "6s", "7s"], ["4c", "4d", "4h"]]
    dw, *_ = card_games.layoff_deadwood(hand, opp_melds, True)
    assert dw == 2


def _test_timing() -> None:
    tot_cpp_time, tot_py_time = 0.0, 0.0
    for i in range(1_000_000):
        cpp_time, py_time = _test_deadwood()
        tot_cpp_time += cpp_time
        tot_py_time += py_time
        if (i + 1) % 100_000 == 0:
            print(
                f"thru {i+1} tests. "
                f"{tot_cpp_time=:.1f}s, {tot_py_time=:.1f}s"
            )


def _test_4melds() -> None:
    cpp_time, py_time = _test_hand(
        ["Kd", "Kc", "Kh", "Ks", "Ah", "2h", "3h", "4h", "3d", "Td"]
    )
    print(
        f"c++: {1_000_000*cpp_time:.0f} micros, "
        f"py: {1_000_000*py_time:.0f} micros"
    )


if __name__ == "__main__":
    # _test_layoffs()
    # _test_timing()
    _test_4melds()
