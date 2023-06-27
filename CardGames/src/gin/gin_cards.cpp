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

    // Deal n cards to each player
    Cards player1_hand = Cards(deck.begin(), deck.begin() + n);
    Cards player2_hand = Cards(deck.begin() + n, deck.begin() + 2 * n);

    // Deal one card to the discard pile
    Cards discard_pile = Cards(deck.begin() + 2 * n, deck.begin() + 2 * n + 1);

    // The rest of the deck
    Cards rest_of_deck = Cards(deck.begin() + 2 * n + 1, deck.end());

    return GinCards(player1_hand, player2_hand, discard_pile, rest_of_deck);
}