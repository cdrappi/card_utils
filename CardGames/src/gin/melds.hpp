// melds.hpp
#pragma once
#include <algorithm>
#include <iostream>
#include <map>
#include <tuple>
#include <vector>
#include <set>
#include <unordered_set>
#include <unordered_map>
#include <numeric>
#include <gperftools/profiler.h>

#include "../deck/card.hpp"

using Ranks = std::vector<Rank>;
using CardSet = std::unordered_set<Card, CardHasher>;
using SortedCardSet = std::set<Card>;
using Melds = std::vector<CardSet>;
using RankValues = std::vector<int>;
using SortedSplitHand = std::tuple<int, std::vector<Cards>, Cards>;
using CardIds = std::array<int, 52>;
using SplitHand = std::tuple<int, CardIds, Cards>;

std::array<std::vector<Suit>, 13> RankPartition(const std::vector<Card> &cards);
std::array<std::vector<Rank>, 4> SuitPartition(const std::vector<Card> &cards);

SortedSplitHand SplitMelds(const Cards &hand, const std::optional<Melds> &melds = std::nullopt);
std::vector<SplitHand> GetCandidateMelds(const Cards &hand, std::optional<int> max_deadwood = std::nullopt, bool stop_on_gin = true);

template <typename T>
std::vector<std::vector<T>> Powerset(const std::vector<T> &set, int index = 0);

std::vector<Cards> SortMelds(const Melds &melds);
std::tuple<std::vector<Rank>, std::unordered_map<Suit, std::vector<std::pair<Rank, Rank>>>>
SplitSetsRuns(const std::vector<std::vector<Card>> &melds);

Cards GetSetLayoffs(const Cards &hand, const std::vector<Rank> &sets);

std::vector<Ranks> GetSuitRunLayoffs(
    const Ranks &suit_ranks,
    const std::vector<std::pair<Rank, Rank>> &suit_runs);

std::vector<Cards> GetRunLayoffs(const Cards &hand, const std::unordered_map<Suit, std::vector<std::pair<Rank, Rank>>> &runs);

std::vector<Cards> MeldIdsToMelds(const CardIds &meld_ids);
std::tuple<int, std::vector<Cards>, Cards, Cards> SortLayoffCandidate(std::tuple<int, Melds, Cards, Cards> candidate);
std::tuple<int, std::vector<Cards>, Cards, Cards> LayoffDeadwood(
    const Cards &hand,
    const Melds &opp_melds,
    bool stop_on_zero = true);
