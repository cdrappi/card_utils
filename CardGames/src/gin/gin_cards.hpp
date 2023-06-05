// gin_cards.hpp
#pragma once

#include <vector>

#include "../deck/card.hpp"
#include "melds.hpp"

class GinCards
{
public:
    Cards player1_hand;
    Cards player2_hand;
    Cards discard_pile;
    Cards deck;
};

GinCards DealHands(int n);
