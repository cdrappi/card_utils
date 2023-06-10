// deck.cpp
#include <algorithm>
#include <random>

#include "card.hpp"
#include "deck.hpp"

Cards OrderedDeck()
{
    Cards deck;

    // Create a standard deck
    for (int s = CLUBS; s <= SPADES; ++s)
    {
        for (int r = ACE; r <= KING; ++r)
        {
            deck.push_back(Card(static_cast<Rank>(r), static_cast<Suit>(s)));
        }
    }
    return deck;
}

Cards ShuffledDeck()
{
    Cards deck = OrderedDeck();

    // Shuffle the deck
    std::random_device rd;
    std::mt19937 g(rd());
    std::shuffle(deck.begin(), deck.end(), g);

    return deck;
}
