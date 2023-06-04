// suit.hpp
#pragma once

enum Rank
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