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
    static void SortByRank(std::vector<Card> &cards);
    std::string ToString() const;
    static Card FromString(std::string card);
};

std::vector<Card> FromStrings(std::vector<std::string> cards);