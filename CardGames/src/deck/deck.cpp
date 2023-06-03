// deck.cpp
#include <algorithm>
#include <random>

#include "card.hpp"
#include "deck.hpp"

std::vector<Card> ShuffledDeck()
{
    std::vector<Card> deck;

    // Create a standard deck
    for (int s = CLUBS; s <= SPADES; ++s)
    {
        for (int r = ACE; r < KING; ++r)
        {
            deck.push_back(Card(static_cast<Rank>(r), static_cast<Suit>(s)));
        }
    }

    // Shuffle the deck
    std::random_device rd;
    std::mt19937 g(rd());
    std::shuffle(deck.begin(), deck.end(), g);

    return deck;
}