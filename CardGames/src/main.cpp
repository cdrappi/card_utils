#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "gin/gin_rummy.hpp"
#include "gin/melds.hpp"

using CardStrings = std::vector<std::string>;

int get_deadwood(std::vector<std::string> &unmelded_cards)
{
    std::vector<Card> cards = FromStrings(unmelded_cards);
    return GinRummyCardsDeadwood(cards);
}

std::tuple<int, std::vector<CardStrings>, CardStrings> SerializeSplitMelds(SplitHand split_melds)
{
    int deadwood = std::get<0>(split_melds);
    std::vector<Cards> melded_cards = std::get<1>(split_melds);
    std::vector<CardStrings> melded_cards_strings;
    for (auto meld : melded_cards)
    {
        melded_cards_strings.push_back(ToStrings(meld));
    }

    Cards unmelded = std::get<2>(split_melds);
    return {deadwood, melded_cards_strings, ToStrings(unmelded)};
}

std::tuple<int, std::vector<CardStrings>, CardStrings> split_melds(std::vector<std::string> &hand, std::optional<std::vector<std::vector<std::string>>> melds = std::nullopt)
{
    std::vector<Card> cards = FromStrings(hand);
    std::optional<Melds> melds_set = std::nullopt;
    if (melds.has_value())
    {
        melds_set = std::make_optional<Melds>();
        for (auto meld : melds.value())
        {
            Cards cards_meld = FromStrings(meld);
            melds_set.value().push_back(CardSet(cards_meld.begin(), cards_meld.end()));
        }
    }

    SplitHand split_melds = SplitMelds(cards, melds_set);
    return SerializeSplitMelds(split_melds);
}

std::vector<std::tuple<int, std::vector<CardStrings>, CardStrings>> all_candidate_melds(std::vector<std::string> &hand)
{
    std::vector<Card> cards = FromStrings(hand);
    std::vector<SplitHand> candidate_melds = GetCandidateMelds(cards);
    std::vector<std::tuple<int, std::vector<CardStrings>, CardStrings>> serialized_candidate_melds;
    for (auto candidate_meld : candidate_melds)
    {
        serialized_candidate_melds.push_back(SerializeSplitMelds(candidate_meld));
    }
    return serialized_candidate_melds;
}

namespace py = pybind11;

PYBIND11_MODULE(card_games, m)
{
    m.def("get_deadwood", &get_deadwood, py::arg("unmelded_cards"), "Get deadwood from list of unmelded cards");
    m.def("split_melds", &split_melds, py::arg("hand"), py::arg("melds") = std::nullopt, "Split melds from list of cards");
    m.def("get_candidate_melds", &all_candidate_melds, py::arg("hand"), "Get all candidate melds from list of cards");
}
