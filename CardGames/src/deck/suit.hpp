// suit.hpp
#pragma once

enum class Suit
{
    CLUBS,
    DIAMONDS,
    HEARTS,
    SPADES
};

Suit CharToSuit(char ch);
char SuitToChar(Suit suit);
