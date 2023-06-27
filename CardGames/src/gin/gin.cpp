#include "gin.hpp"

bool IsP1Draw(GinTurn turn)
{
    return turn == GinTurn::P1_DRAWS_FIRST || turn == GinTurn::P1_DRAWS_FROM_DECK || turn == GinTurn::P1_DRAWS;
}

bool IsP2Draw(GinTurn turn)
{
    return turn == GinTurn::P2_DRAWS_FIRST || turn == GinTurn::P2_DRAWS_FROM_DECK || turn == GinTurn::P2_DRAWS;
}

bool IsP1Turn(GinTurn turn)
{
    return turn == GinTurn::P1_DRAWS_FIRST || turn == GinTurn::P1_DRAWS_FROM_DECK || turn == GinTurn::P1_DRAWS || turn == GinTurn::P1_DISCARDS || turn == GinTurn::P1_MAY_KNOCK;
}

std::string TurnToString(GinTurn turn)
{
    switch (turn)
    {
    case GinTurn::P1_DRAWS_FIRST:
        return "P1_DRAWS_FIRST";
    case GinTurn::P2_DRAWS_FIRST:
        return "P2_DRAWS_FIRST";
    case GinTurn::P1_DRAWS_FROM_DECK:
        return "P1_DRAWS_FROM_DECK";
    case GinTurn::P2_DRAWS_FROM_DECK:
        return "P2_DRAWS_FROM_DECK";
    case GinTurn::P1_DRAWS:
        return "P1_DRAWS";
    case GinTurn::P2_DRAWS:
        return "P2_DRAWS";
    case GinTurn::P1_DISCARDS:
        return "P1_DISCARDS";
    case GinTurn::P2_DISCARDS:
        return "P2_DISCARDS";
    case GinTurn::P1_MAY_KNOCK:
        return "P1_MAY_KNOCK";
    case GinTurn::P2_MAY_KNOCK:
        return "P2_MAY_KNOCK";
    default:
        throw std::invalid_argument("Invalid turn");
    }
}

std::string ActionToString(GinAction action)
{
    switch (action)
    {
    case GinAction::PASS:
        return "PASS";
    case GinAction::KNOCK:
        return "KNOCK";
    case GinAction::DONT_KNOCK:
        return "DONT_KNOCK";
    case GinAction::PICK_FROM_DECK:
        return "PICK_FROM_DECK";
    case GinAction::PICK_FROM_DISCARD:
        return "PICK_FROM_DISCARD";
    case GinAction::DISCARD_CARD:
        return "DISCARD_CARD";
    default:
        throw std::invalid_argument("Invalid action");
    }
}