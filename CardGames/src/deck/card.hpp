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
    int ToId() const;
    bool operator<(Card other) const;
};

bool operator==(Card first, Card second);
bool operator!=(Card first, Card second);

void SortByRank(std::vector<Card> &cards);
Card CardFromId(int card_id);
Card CardFromString(const std::string &card);
std::vector<Card> FromStrings(const std::vector<std::string> &cards);
std::vector<std::string> ToStrings(const std::vector<Card> &cards);

using Cards = std::vector<Card>;

struct CardHasher
{
    std::size_t operator()(const Card &card) const
    {
        return std::hash<int>()(card.ToId());
    }
};
