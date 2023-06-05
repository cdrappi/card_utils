// gin_cards.cpp
#include "gin_cards.hpp"

#include "../deck/card.hpp"
#include "../deck/deck.hpp"
#include <algorithm>
#include <random>

GinCards DealHands(int n)
{

    // Create a standard deck
    Cards deck = ShuffledDeck();

    // Create the GinCards object
    GinCards gin_cards;

    // Deal n cards to each player
    gin_cards.player1_hand = Cards(deck.begin(), deck.begin() + n);
    gin_cards.player2_hand = Cards(deck.begin() + n, deck.begin() + 2 * n);

    // Deal one card to the discard pile
    gin_cards.discard_pile = Cards(deck.begin() + 2 * n, deck.begin() + 2 * n + 1);

    // The rest of the deck
    gin_cards.deck = Cards(deck.begin() + 2 * n + 1, deck.end());

    return gin_cards;
}