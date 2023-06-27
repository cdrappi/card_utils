

#include "rank.hpp"

Rank CharToRank(char ch)
{
    std::map<char, Rank> lookup = {
        {'A', Rank::ACE},
        {'2', Rank::TWO},
        {'3', Rank::THREE},
        {'4', Rank::FOUR},
        {'5', Rank::FIVE},
        {'6', Rank::SIX},
        {'7', Rank::SEVEN},
        {'8', Rank::EIGHT},
        {'9', Rank::NINE},
        {'T', Rank::TEN},
        {'J', Rank::JACK},
        {'Q', Rank::QUEEN},
        {'K', Rank::KING},
    };

    auto it = lookup.find(ch);
    if (it != lookup.end())
        return it->second;

    std::stringstream ss;
    ss << "Invalid rank: " << ch;
    throw std::invalid_argument(ss.str());
}

char RankToChar(Rank rank)
{
    std::map<Rank, char> lookup = {
        {Rank::ACE, 'A'},
        {Rank::TWO, '2'},
        {Rank::THREE, '3'},
        {Rank::FOUR, '4'},
        {Rank::FIVE, '5'},
        {Rank::SIX, '6'},
        {Rank::SEVEN, '7'},
        {Rank::EIGHT, '8'},
        {Rank::NINE, '9'},
        {Rank::TEN, 'T'},
        {Rank::JACK, 'J'},
        {Rank::QUEEN, 'Q'},
        {Rank::KING, 'K'},
    };

    auto it = lookup.find(rank);
    if (it != lookup.end())
        return it->second;

    // std::cout << "invalid rank: " << int(rank);
    throw std::invalid_argument("Invalid rank enum value");
}

Rank ValueToRank(int value)
{
    if (value < int(Rank::ACE) || value > int(Rank::KING) + 1)
        throw std::invalid_argument("Invalid rank value");
    if (value == int(Rank::KING) + 1)
        return Rank::ACE;
    return static_cast<Rank>(value);
}

int RankToIndex(Rank rank)
{
    return ((int(rank) + 12) % 13);
}