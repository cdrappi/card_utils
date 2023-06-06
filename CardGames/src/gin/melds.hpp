// melds.hpp
#pragma once
#include <vector>
#include <tuple>
#include <set>
#include <map>
#include <set>
#include <unordered_map>

#include "../deck/card.hpp"

using Ranks = std::vector<Rank>;
using CardSet = std::set<Card>;
using Melds = std::vector<CardSet>;
using RankValues = std::vector<int>;
using SplitHand = std::tuple<int, std::vector<Cards>, Cards>;

std::map<Rank, std::vector<Suit>> RankPartition(const std::vector<Card> &cards);
std::map<Suit, std::vector<Rank>> SuitPartition(const std::vector<Card> &cards);

SplitHand SplitMelds(const Cards &hand, std::optional<Melds> melds = std::nullopt);
std::vector<SplitHand> GetCandidateMelds(const Cards &hand, std::optional<int> max_deadwood = std::nullopt, bool stop_on_gin = true);

std::vector<Cards> CardsPowerset(const Cards &set, int index = 0);

std::tuple<std::vector<Rank>, std::map<Suit, std::vector<std::pair<Rank, Rank>>>>
SplitSetsRuns(std::vector<std::vector<Card>> melds);

Cards GetSetLayoffs(Cards hand, std::vector<Rank> sets);

std::vector<Ranks> GetSuitRunLayoffs(
    Ranks suit_ranks,
    std::vector<std::pair<Rank, Rank>> suit_runs);

Cards GetRunLayoffs(Cards hand, std::unordered_map<Suit, std::vector<std::pair<Rank, Rank>>> runs);

std::tuple<int, std::vector<Cards>, Cards, Cards> LayoffDeadwood(
    Cards hand,
    Melds opp_melds,
    bool stop_on_zero = true);
