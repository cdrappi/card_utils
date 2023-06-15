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
    GinCards(
        Cards player1_hand,
        Cards player2_hand,
        Cards discard_pile,
        Cards deck)
        : player1_hand(player1_hand),
          player2_hand(player2_hand),
          discard_pile(discard_pile),
          deck(deck){};
};

GinCards DealHands(int n);
