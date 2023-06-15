// card.cpp
#include <algorithm>
#include <string>
#include <vector>

#include "card.hpp"
#include "rank.hpp"
#include "suit.hpp"

void SortByRank(std::vector<Card> &cards)
{
    std::sort(cards.begin(), cards.end(), [](const Card &a, const Card &b)
              { return a.rank < b.rank; });
}

std::string Card::ToString() const
{
    std::string cardString;
    cardString += RankToChar(rank);
    cardString += SuitToChar(suit);
    return cardString;
}

Card Card::FromId(int card_id)
{
    Suit suit = Suit(card_id % 4);
    // Rank(ACE) = 0
    // ID(As) = 51 so: (51 / 4 + 1) % 13 = 0
    // Rank(2) = 1
    // ID(2c) = 0  so: (0 / 4 + 1) % 13 = 1
    Rank rank = Rank((card_id / 4 + 1) % 13);
    return Card(rank, suit);
}

bool Card::operator<(const Card &other) const
{
    if (rank != other.rank)
    {
        return rank < other.rank;
    }
    return suit < other.suit;
}

bool Card::operator==(const Card &other) const
{
    return rank == other.rank && suit == other.suit;
}

static Card FromString(std::string card)
{
    return Card(CharToRank(card[0]), CharToSuit(card[1]));
}

std::vector<Card> FromStrings(std::vector<std::string> cards)
{
    std::vector<Card> cardObjects;
    for (const auto &card : cards)
    {
        cardObjects.push_back(FromString(card));
    }
    return cardObjects;
}

std::vector<std::string> ToStrings(const std::vector<Card> &cards)
{
    std::vector<std::string> cardStrings;
    for (const auto &card : cards)
    {
        cardStrings.push_back(card.ToString());
    }
    return cardStrings;
}