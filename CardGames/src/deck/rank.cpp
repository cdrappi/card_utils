#include <map>
#include <stdexcept>
#include <sstream>

#include "rank.hpp"

Rank CharToRank(char ch)
{
    std::map<char, Rank> lookup = {
        {'A', ACE},
        {'2', TWO},
        {'3', THREE},
        {'4', FOUR},
        {'5', FIVE},
        {'6', SIX},
        {'7', SEVEN},
        {'8', EIGHT},
        {'9', NINE},
        {'T', TEN},
        {'J', JACK},
        {'Q', QUEEN},
        {'K', KING},
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
        {ACE, 'A'},
        {TWO, '2'},
        {THREE, '3'},
        {FOUR, '4'},
        {FIVE, '5'},
        {SIX, '6'},
        {SEVEN, '7'},
        {EIGHT, '8'},
        {NINE, '9'},
        {TEN, 'T'},
        {JACK, 'J'},
        {QUEEN, 'Q'},
        {KING, 'K'},
    };

    auto it = lookup.find(rank);
    if (it != lookup.end())
        return it->second;

    throw std::invalid_argument("Invalid rank enum value");
}

Rank ValueToRank(int value)
{
    if (value < ACE || value > KING + 1)
        throw std::invalid_argument("Invalid rank value");
    if (value == KING + 1)
        return ACE;
    return static_cast<Rank>(value);
}