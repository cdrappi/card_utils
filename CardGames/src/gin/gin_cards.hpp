// gin_cards.hpp
#pragma once

#include "../deck/card.hpp"
#include <vector>

class GinCards
{
public:
    std::vector<Card> player1_hand;
    std::vector<Card> player2_hand;
    std::vector<Card> discard_pile;
    std::vector<Card> deck;
};

GinCards DealHands(int n);
