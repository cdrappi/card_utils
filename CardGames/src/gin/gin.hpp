// gin.hpp
#pragma once

enum GinTurn
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

enum GinEnding
{
    P1_KNOCKS,
    P2_KNOCKS,
    P1_GINS,
    P2_GINS,
    PLAYED_TO_THE_WALL,
};

enum GinAction
{
    PICK_FROM_DECK,
    PICK_FROM_DISCARD,
    DISCARD_CARD,
    KNOCK,
    PASS,
};

enum GinHud
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
