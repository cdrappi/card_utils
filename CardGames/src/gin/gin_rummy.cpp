#include "gin_rummy.hpp"

int GinRummyRankDeadwood(Rank rank)
{
    switch (rank)
    {
    case Rank::TEN:
    case Rank::JACK:
    case Rank::QUEEN:
    case Rank::KING:
        return 10;
    default:
        // ace has value 0 and 9 has value 8,
        // so add 1 to all the raw ranks
        return static_cast<int>(rank + 1);
    }
}

int GinRummyCardsDeadwood(std::vector<Card> &unmelded_cards)
{
    int deadwood = 0;
    for (Card card : unmelded_cards)
    {
        deadwood += GinRummyRankDeadwood(card.rank);
    }
    return deadwood;
}
