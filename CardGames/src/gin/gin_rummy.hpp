#include <vector>
#include <unordered_map>
#include <optional>

#include "../deck/card.hpp"
#include "../deck/rank.hpp"
#include "gin.hpp"
#include "gin_cards.hpp"

int GinRummyRankDeadwood(Rank rank);
int GinRummyCardsDeadwood(const std::vector<Card> &unmelded_cards);

class AbstractGinGameState
{
public:
    const int cards_dealt = 10;
    const int end_cards_in_deck = 2;
    const int undercut_bonus = 20;
    const int gin_bonus = 20;
    const int big_gin_bonus = 30;
    const int max_shuffles = 1;

    AbstractGinGameState(
        GinCards cards,
        GinTurn turn,
        GinTurn first_turn,
        std::optional<std::unordered_map<Card, GinHud>> public_hud = std::nullopt,
        std::optional<Card> last_draw_from_discard = std::nullopt,
        bool is_complete = false,
        int shuffles = 0);

    void FirstTurnPass();
    Card DrawCard(bool from_discard);
    void DiscardCard(Card card);
    void DecideKnock(bool knocks, std::optional<Melds> melds = std::nullopt);
    void EndGame(GinEnding how, int p1_deadwood, int p2_deadwood);
    Card TopOfDiscard();
    Card TopOfDeck();
    std::unordered_map<Card, GinHud> PlayerHud(bool p1);
    static int GetDeadwood(
        const Cards hand,
        std::optional<Melds> melds = std::nullopt,
        std::optional<Melds> opp_melds = std::nullopt);
    static Cards SortHand(const Cards hand);

private:
    GinCards cards;
    GinTurn turn;
    GinTurn first_turn;
    std::unordered_map<Card, GinHud> public_hud;
    std::optional<Card> last_draw_from_discard;
    bool is_complete;
    int shuffles;
    int p1_score;
    int p2_score;

    bool HitMaxShuffles();
    void AddToHand(bool p1, Card card);
    GinTurn AdvanceTurn(GinTurn current, bool from_discard = false, int deadwood = 11);
};

void RemoveCard(Cards &cards, Card card);