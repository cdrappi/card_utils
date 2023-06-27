// suit.hpp
#pragma once

#include <map>
#include <stdexcept>
#include <sstream>
#include <iostream>

enum class Rank
{
    ACE,
    TWO,
    THREE,
    FOUR,
    FIVE,
    SIX,
    SEVEN,
    EIGHT,
    NINE,
    TEN,
    JACK,
    QUEEN,
    KING
};

Rank CharToRank(char ch);
char RankToChar(Rank rank);
Rank ValueToRank(int value);

int RankToIndex(Rank rank);