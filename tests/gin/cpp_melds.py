from card_utils.games.gin.rummy.utils import deal_new_game, split_melds
import card_games


def _test_deadwood() -> None:
    new_game = deal_new_game()
    hand = new_game["p1_hand"]

    cpp_dw, cpp_melds, cpp_um = card_games.split_melds(hand, None)
    py_dw, py_melds, py_um = split_melds(hand)
    if cpp_dw != py_dw:
        print(f"deadwoods do not match: {cpp_dw=}, {py_dw=}")
        print(f"cpp unmelded: {cpp_um}")
        print(f"py unmelded: {py_um}")
        raise ValueError("cpp_dw != py_dw")


def test_layoffs() -> None:
    hand = ["5c", "5d", "5h", "3s", "4s", "5s", "Ac", "Ad", "4h", "7s"]
    opp_melds = [["3h", "3d", "3c"], ["7c", "7d", "7h"]]
    dw, *_ = card_games.layoff_deadwood(hand, opp_melds, True)
    assert dw == 6

    hand = ["5c", "5d", "5h", "9d", "Td", "Jd", "3s", "4s", "Ac", "Ad"]
    opp_melds = [["5s", "6s", "7s"], ["7c", "7d", "7h"]]
    dw, *_ = card_games.layoff_deadwood(hand, opp_melds, True)
    assert dw == 2

    hand = ["5c", "5d", "5h", "9d", "Td", "Jd", "3s", "4s", "Ac", "Ad"]
    opp_melds = [["5s", "6s", "7s"], ["4c", "4d", "4h"]]
    dw, *_ = card_games.layoff_deadwood(hand, opp_melds, True)
    assert dw == 2


if __name__ == "__main__":
    test_layoffs()
    for i in range(1_000_000):
        _test_deadwood()
        if (i + 1) % 100_000 == 0:
            print(f"thru {i+1} tests")
