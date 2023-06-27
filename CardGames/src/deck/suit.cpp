#include <map>
#include <stdexcept>
#include <sstream>

#include "suit.hpp"

Suit CharToSuit(char ch)
{
    std::map<char, Suit> lookup = {
        {'c', Suit::CLUBS},
        {'d', Suit::DIAMONDS},
        {'h', Suit::HEARTS},
        {'s', Suit::SPADES}};

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
        {Suit::CLUBS, 'c'},
        {Suit::DIAMONDS, 'd'},
        {Suit::HEARTS, 'h'},
        {Suit::SPADES, 's'},
    };

    auto it = lookup.find(suit);
    if (it != lookup.end())
        return it->second;

    throw std::invalid_argument("Invalid suit enum value");
}