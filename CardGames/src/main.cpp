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

std::tuple<int, std::vector<CardStrings>, CardStrings> SerializeSplitMelds(SortedSplitHand split_melds)
{
    int deadwood = std::get<0>(split_melds);
    std::vector<Cards> melded_cards = std::get<1>(split_melds);
    std::vector<CardStrings> melded_cards_strings;
    for (auto meld : melded_cards)
        melded_cards_strings.push_back(ToStrings(meld));

    Cards unmelded = std::get<2>(split_melds);
    SortByRank(unmelded);
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

    SortedSplitHand split_melds = SplitMelds(cards, melds_set);
    return SerializeSplitMelds(split_melds);
}

std::vector<std::tuple<int, std::vector<CardStrings>, CardStrings>> all_candidate_melds(std::vector<std::string> &hand)
{
    std::vector<Card> cards = FromStrings(hand);
    std::vector<SplitHand> candidate_melds = GetCandidateMelds(cards);
    std::vector<std::tuple<int, std::vector<CardStrings>, CardStrings>> serialized_candidate_melds;
    for (SplitHand candidate_meld : candidate_melds)
    {
        int deadwood = std::get<0>(candidate_meld);
        Melds chosen_melds = std::get<1>(candidate_meld);
        Cards unmelded = std::get<2>(candidate_meld);
        SortedSplitHand sorted_split_hand = SortedSplitHand{deadwood, SortMelds(chosen_melds), unmelded};
        serialized_candidate_melds.push_back(SerializeSplitMelds(sorted_split_hand));
    }
    return serialized_candidate_melds;
}

std::tuple<int, std::vector<CardStrings>, CardStrings, CardStrings>
layoff_deadwood(
    CardStrings hand,
    std::vector<CardStrings> opp_melds,
    bool stop_on_zero)
{
    Melds opp_melds_set;
    for (auto meld : opp_melds)
    {
        Cards cards_meld = FromStrings(meld);
        opp_melds_set.push_back(CardSet(cards_meld.begin(), cards_meld.end()));
    }
    auto dw = LayoffDeadwood(FromStrings(hand), opp_melds_set, stop_on_zero);
    std::vector<Cards> melded_cards = std::get<1>(dw);
    std::vector<CardStrings> melded_cards_strings;
    for (auto meld : melded_cards)
    {
        melded_cards_strings.push_back(ToStrings(meld));
    }
    return {std::get<0>(dw), melded_cards_strings, ToStrings(std::get<2>(dw)), ToStrings(std::get<3>(dw))};
}

namespace py = pybind11;

PYBIND11_MODULE(card_games, m)
{
    m.def("get_deadwood", &get_deadwood, py::arg("unmelded_cards"), "Get deadwood from list of unmelded cards");
    m.def("split_melds", &split_melds, py::arg("hand"), py::arg("melds") = std::nullopt, "Split melds from list of cards");
    m.def("get_candidate_melds", &all_candidate_melds, py::arg("hand"), "Get all candidate melds from list of cards");
    m.def("layoff_deadwood", &layoff_deadwood, py::arg("hand"), py::arg("opp_melds"), py::arg("stop_on_zero") = true, "Layoff deadwood from list of cards");
}
