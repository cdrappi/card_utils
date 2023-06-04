from card_utils.games.gin.rummy.utils import deal_new_game, split_melds
import card_games


def _single_test() -> None:
    new_game = deal_new_game()
    hand = new_game["p1_hand"]

    cpp_dw, cpp_melds, cpp_um = card_games.split_melds(hand, None)
    py_dw, py_melds, py_um = split_melds(hand)
    if cpp_dw != py_dw:
        print(f"deadwoods do not match: {cpp_dw=}, {py_dw=}")
        print(f"cpp unmelded: {cpp_um}")
        print(f"py unmelded: {py_um}")
        raise ValueError("cpp_dw != py_dw")


if __name__ == "__main__":
    for i in range(1_000_000):
        _single_test()
        if (i + 1) % 100_000 == 0:
            print(f"thru {i+1} tests")
