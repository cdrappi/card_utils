// deck.cpp
#include <algorithm>
#include <random>

#include "card.hpp"
#include "deck.hpp"

Cards OrderedDeck()
{
    Cards deck;
    for (auto r : ALL_RANKS)
        for (auto s : ALL_SUITS)
            deck.push_back(Card(r, s));
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
