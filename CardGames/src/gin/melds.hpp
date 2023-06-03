// melds.hpp
#pragma once
#include <vector>
#include <tuple>
#include "../deck/card.hpp"

std::map<Rank, std::vector<Suit>> RankPartition(const std::vector<Card> &cards);
std::map<Suit, std::vector<Rank>> SuitPartition(const std::vector<Card> &cards);

std::tuple<std::vector<std::vector<Card>>, std::vector<std::vector<Card>>> FindSets(const std::vector<Card> &cards);
