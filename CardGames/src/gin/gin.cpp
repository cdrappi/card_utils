#include "gin.hpp"

bool IsP1Draw(GinTurn turn)
{
    return turn == P1_DRAWS_FIRST || turn == P1_DRAWS_FROM_DECK || turn == P1_DRAWS;
}

bool IsP2Draw(GinTurn turn)
{
    return turn == P2_DRAWS_FIRST || turn == P2_DRAWS_FROM_DECK || turn == P2_DRAWS;
}
