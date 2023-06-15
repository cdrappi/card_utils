#include "gin.hpp"

bool IsP1Draw(GinTurn turn)
{
    return turn == P1_DRAWS_FIRST || turn == P1_DRAWS_FROM_DECK || turn == P1_DRAWS;
}

bool IsP2Draw(GinTurn turn)
{
    return turn == P2_DRAWS_FIRST || turn == P2_DRAWS_FROM_DECK || turn == P2_DRAWS;
}

bool IsP1Turn(GinTurn turn)
{
    return turn == P1_DRAWS_FIRST || turn == P1_DRAWS_FROM_DECK || turn == P1_DRAWS || turn == P1_DISCARDS || turn == P1_MAY_KNOCK;
}