// gin.hpp
#pragma once
#include <map>
#include <string>

#include "../deck/card.hpp"

enum class GinTurn
{
    P1_DRAWS_FIRST,
    P2_DRAWS_FIRST,

    P1_DRAWS_FROM_DECK,
    P2_DRAWS_FROM_DECK,

    P1_DRAWS,
    P2_DRAWS,

    P1_DISCARDS,
    P2_DISCARDS,

    P1_MAY_KNOCK,
    P2_MAY_KNOCK
};

bool IsP1Draw(GinTurn turn);
bool IsP2Draw(GinTurn turn);

bool IsP1Turn(GinTurn turn);

std::string TurnToString(GinTurn turn);

enum class GinEnding
{
    P1_KNOCKS,
    P2_KNOCKS,
    P1_GINS,
    P2_GINS,
    P1_BIG_GINS,
    P2_BIG_GINS,
    PLAYED_TO_THE_WALL,
};

enum class GinAction
{
    PASS,
    KNOCK,
    DONT_KNOCK,
    PICK_FROM_DECK,
    PICK_FROM_DISCARD,
    DISCARD_CARD,
};

std::string ActionToString(GinAction action);

enum class GinHud
{
    // in user's hand
    USER = 0,
    // user knows for sure card is in opponents hand
    OPPONENT = 1,
    TOP_OF_DISCARD_PILE = 2,
    IN_DISCARD_PILE = 3,
    // in opponent hand or deck
    LIVE = 4,
    // we have simmed this card to be in opponent's hand
    OPPONENT_SIMMED = 5,
    // for admin-only view
    PLAYER_1 = 6,
    PLAYER_2 = 7,
    DECK = 8,
};

using CardsHud = std::map<Card, GinHud>;
