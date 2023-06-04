// card.hpp
#pragma once

#include <vector>

#include "rank.hpp"
#include "suit.hpp"

class Card
{
public:
    Rank rank;
    Suit suit;
    Card(Rank r, Suit s) : rank(r), suit(s) {}
    std::string ToString() const;
    static Card FromString(std::string card);
    bool operator<(const Card &other) const;
};

void SortByRank(std::vector<Card> &cards);
std::vector<Card> FromStrings(std::vector<std::string> cards);
std::vector<std::string> ToStrings(const std::vector<Card> &cards);
