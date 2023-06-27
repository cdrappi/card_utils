// suit.hpp
#pragma once
#include <vector>

enum class Suit
{
    CLUBS,
    DIAMONDS,
    HEARTS,
    SPADES
};

Suit CharToSuit(char ch);
char SuitToChar(Suit suit);

const std::vector<Suit> ALL_SUITS = {Suit::CLUBS, Suit::DIAMONDS, Suit::HEARTS, Suit::SPADES};