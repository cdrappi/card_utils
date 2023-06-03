#include <map>
#include <stdexcept>
#include <sstream>

#include "suit.hpp"

Suit CharToSuit(char ch)
{
    std::map<char, Suit> lookup = {
        {'c', CLUBS},
        {'d', DIAMONDS},
        {'h', HEARTS},
        {'s', SPADES}};

    auto it = lookup.find(ch);
    if (it != lookup.end())
        return it->second;

    std::stringstream ss;
    ss << "Invalid suit: " << ch;
    throw std::invalid_argument(ss.str());
}

char SuitToChar(Suit suit)
{
    std::map<Suit, char> lookup = {
        {CLUBS, 'c'},
        {DIAMONDS, 'd'},
        {HEARTS, 'h'},
        {SPADES, 's'},
    };

    auto it = lookup.find(suit);
    if (it != lookup.end())
        return it->second;

    throw std::invalid_argument("Invalid suit enum value");
}