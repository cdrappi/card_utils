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

std::string TurnToString(GinTurn turn)
{
    switch (turn)
    {
    case P1_DRAWS_FIRST:
        return "P1_DRAWS_FIRST";
    case P2_DRAWS_FIRST:
        return "P2_DRAWS_FIRST";
    case P1_DRAWS_FROM_DECK:
        return "P1_DRAWS_FROM_DECK";
    case P2_DRAWS_FROM_DECK:
        return "P2_DRAWS_FROM_DECK";
    case P1_DRAWS:
        return "P1_DRAWS";
    case P2_DRAWS:
        return "P2_DRAWS";
    case P1_DISCARDS:
        return "P1_DISCARDS";
    case P2_DISCARDS:
        return "P2_DISCARDS";
    case P1_MAY_KNOCK:
        return "P1_MAY_KNOCK";
    case P2_MAY_KNOCK:
        return "P2_MAY_KNOCK";
    default:
        throw std::invalid_argument("Invalid turn");
    }
}

std::string ActionToString(GinAction action)
{
    switch (action)
    {
    case PASS:
        return "PASS";
    case KNOCK:
        return "KNOCK";
    case DONT_KNOCK:
        return "DONT_KNOCK";
    case PICK_FROM_DECK:
        return "PICK_FROM_DECK";
    case PICK_FROM_DISCARD:
        return "PICK_FROM_DISCARD";
    case DISCARD_CARD:
        return "DISCARD_CARD";
    default:
        throw std::invalid_argument("Invalid action");
    }
}