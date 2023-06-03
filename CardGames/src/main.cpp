#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "gin/gin_rummy.hpp"

int add(int i, int j)
{
    return i + j;
}

int get_deadwood(std::vector<std::string> &unmelded_cards)
{
    std::vector<Card> cards = FromStrings(unmelded_cards);
    return GinRummyCardsDeadwood(cards);
}

namespace py = pybind11;

PYBIND11_MODULE(card_games, m)
{
    m.def("add", &add, "A function which adds two numbers");
    m.def("get_deadwood", &get_deadwood, "Get deadwood from list of unmelded cards");
}