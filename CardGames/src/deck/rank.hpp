// suit.hpp
#pragma once

#include <map>
#include <stdexcept>
#include <sstream>
#include <iostream>
#include <vector>

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

const std::vector<Rank> ALL_RANKS = {
    Rank::TWO,
    Rank::THREE,
    Rank::FOUR,
    Rank::FIVE,
    Rank::SIX,
    Rank::SEVEN,
    Rank::EIGHT,
    Rank::NINE,
    Rank::TEN,
    Rank::JACK,
    Rank::QUEEN,
    Rank::KING,
    Rank::ACE};