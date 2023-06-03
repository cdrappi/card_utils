// card.cpp
#include <algorithm>
#include <string>
#include <vector>

#include "card.hpp"
#include "rank.hpp"
#include "suit.hpp"

void Card::SortByRank(std::vector<Card> &cards)
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