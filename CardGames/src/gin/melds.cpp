// melds.cpp

#include <algorithm>
#include <map>

#include "melds.hpp"
#include "../deck/card.hpp"
#include "../deck/rank.hpp"
#include "../deck/suit.hpp"

std::map<Rank, std::vector<Suit>> RankPartition(const std::vector<Card> &cards)
{
    std::map<Rank, std::vector<Suit>> rankToSuitsMap;

    // Group the cards by rank
    for (const auto &card : cards)
    {
        rankToSuitsMap[card.rank].push_back(card.suit);
    }

    return rankToSuitsMap;
}

std::map<Suit, std::vector<Rank>> SuitPartition(const std::vector<Card> &cards)
{
    std::map<Suit, std::vector<Rank>> suitToRanksMap;

    // Group the cards by suit
    for (const auto &card : cards)
    {
        suitToRanksMap[card.suit].push_back(card.rank);
    }

    return suitToRanksMap;
}

std::tuple<std::vector<std::vector<Card>>, std::vector<std::vector<Card>>> FindSets(const std::vector<Card> &cards)
{
    const auto rankToSuitsMap = RankPartition(cards);

    std::vector<std::vector<Card>> setsOfThree, setsOfFour;

    // Iterate over each rank
    for (const auto &[rank, suits] : rankToSuitsMap)
    {

        // If there are 3 or more cards of the same rank, add them to setsOfThree
        if (suits.size() == 3)
        {
            std::vector<Card> cards;
            for (const auto &suit : suits)
            {
                cards.push_back(Card(rank, suit));
            }
            setsOfThree.push_back(std::move(cards));
        }

        // If there are 4 or more cards of the same rank:
        // -> add them to setsOfFour
        // -> add all possible combinations of 3 cards to setsOfThree
        if (suits.size() == 4)
        {
            // add to sets of four
            std::vector<Card> cards;
            for (const auto &suit : suits)
            {
                cards.push_back(Card(rank, suit));
            }
            setsOfFour.push_back(std::move(cards));

            // add all possible combinations of 3 cards to sets of three
            for (const auto &exclude_suit : suits)
            {
                std::vector<Card> cards;
                for (const auto &suit : suits)
                {
                    if (suit != exclude_suit)
                    {
                        cards.push_back(Card(rank, suit));
                    }
                }
                setsOfThree.push_back(std::move(cards));
            }
        }
    }

    return {setsOfThree, setsOfFour};
}