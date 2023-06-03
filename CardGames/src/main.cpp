#include <pybind11/pybind11.h>

enum Suit
{
    CLUBS,
    DIAMONDS,
    HEARTS,
    SPADES
};

enum Rank
{
    ACE = 1,
    TWO,
    THREE,
    FOUR,
    FIVE,
    SIX,
    SEVEN,
    EIGHT,
    NINE,
    TEN,
    JACK,
    QUEEN,
    KING
};

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

// class RummyAction(Enum):
//     DRAW = "draw"
//     DISCARD = "discard"
//     KNOCK = "knock"
//     PASS = "pass"
//     COMPLETE = "complete"
//     WAIT = "wait"

// class RummyHud(Enum):
//     PLAYER_1 = "1"
//     PLAYER_2 = "2"
//     TOP_OF_DISCARD = "t"
//     DISCARD = "d"
//     USER = "u"
//     OPPONENT = "o"

// class RummyEndGame(Enum):
//     KNOCK = "knock"
//     GIN = "gin"
//     WALL = "hit-the-wall"

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

class Card
{
private:
    Rank rank;
    Suit suit;

public:
    Card(Rank r, Suit s) : rank(r), suit(s) {}
    // Rest of your code here
};

int add(int i, int j)
{
    return i + j;
}

namespace py = pybind11;

PYBIND11_MODULE(card_games, m)
{
    m.def("add", &add, "A function which adds two numbers");
}