// melds.hpp
#pragma once
#include <vector>
#include <tuple>
#include <set>
#include "../deck/card.hpp"

using Ranks = std::vector<Rank>;
using Cards = std::vector<Card>;
using CardSet = std::set<Card>;
using Melds = std::vector<CardSet>;
using RankValues = std::vector<int>;
using SplitHand = std::tuple<int, std::vector<Cards>, Cards>;

std::map<Rank, std::vector<Suit>> RankPartition(const std::vector<Card> &cards);
std::map<Suit, std::vector<Rank>> SuitPartition(const std::vector<Card> &cards);

SplitHand SplitMelds(const Cards &hand, std::optional<Melds> melds = std::nullopt);
std::vector<SplitHand> GetCandidateMelds(const Cards &hand, std::optional<int> max_deadwood = std::nullopt, bool stop_on_gin = true);