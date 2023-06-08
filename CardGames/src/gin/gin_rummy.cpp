#include <random>
#include "gin_rummy.hpp"
#include "../deck/deck.hpp"

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

int GinRummyCardsDeadwood(const std::vector<Card> &unmelded_cards)
{
    int deadwood = 0;
    for (Card card : unmelded_cards)
    {
        deadwood += GinRummyRankDeadwood(card.rank);
    }
    return deadwood;
}

GinRummyGameState::GinRummyGameState(
    GinCards cards,
    GinTurn turn,
    GinTurn first_turn,
    std::optional<CardsHud> public_hud,
    std::optional<Card> last_draw_from_discard,
    bool is_complete,
    int shuffles) : cards(cards),
                    turn(turn),
                    first_turn(first_turn),
                    last_draw_from_discard(last_draw_from_discard),
                    is_complete(is_complete),
                    p1_score(0),
                    p2_score(0)
{
    if (public_hud)
    {
        this->public_hud = public_hud.value();
    }
    else
    {
        this->public_hud = {};
        this->public_hud[this->TopOfDiscard()] = GinHud::TOP_OF_DISCARD_PILE;
    }
}

void GinRummyGameState::FirstTurnPass()
{
    // TODO
    if (this->turn != GinTurn::P1_DRAWS_FIRST && this->turn != GinTurn::P2_DRAWS_FIRST)
        throw std::invalid_argument("Cannot pass: it is not your first turn");
    this->turn = this->AdvanceTurn(this->turn);
    if (this->turn == GinTurn::P1_DRAWS_FROM_DECK)
        this->DrawCard(false);
    else if (this->turn == GinTurn::P2_DRAWS_FROM_DECK)
        this->DrawCard(false);
};

Card GinRummyGameState::DrawCard(bool from_discard)
{
    bool p1_draws = IsP1Draw(this->turn);
    bool p2_draws = IsP2Draw(this->turn);
    if (!p1_draws && !p2_draws)
        throw std::invalid_argument("Cannot draw: it is not the player's turn to draw");
    if (p1_draws && (this->cards_dealt != this->cards.player1_hand.size()))
        throw std::invalid_argument("Player 1 cannot draw because they have too many cards");
    if (p2_draws && (this->cards_dealt != this->cards.player2_hand.size()))
        throw std::invalid_argument("Player 2 cannot draw because they have too many cards");

    if (from_discard)
    {
        Card card_drawn = this->TopOfDiscard();
        this->AddToHand(p1_draws, card_drawn);
        this->cards.discard_pile.pop_back();
        this->public_hud[card_drawn] = p1_draws ? GinHud::PLAYER_1 : GinHud::PLAYER_2;
        this->last_draw_from_discard = card_drawn;
        return card_drawn;
    }
    else
    {
        Card card_drawn = this->TopOfDeck();
        this->AddToHand(p1_draws, card_drawn);
        // remove the item at index 0 of the deck
        this->cards.deck.erase(this->cards.deck.begin());
        // TODO: allow big gin
        // Cards hand = p1_draws ? this->cards.player1_hand : this->cards.player2_hand;
        // int deadwood = this->GetDeadwood(hand);
        this->turn = this->AdvanceTurn(this->turn, from_discard, 11);
        this->last_draw_from_discard = std::nullopt;
        return card_drawn;
    }
};

void RemoveCard(Cards &cards, const Card &card)
{
    cards.erase(std::remove(cards.begin(), cards.end(), card), cards.end());
}

bool GinRummyGameState::EndIfHitWall()
{
    if (this->cards.deck.size() == this->end_cards_in_deck)
    {
        this->EndGame(GinEnding::PLAYED_TO_THE_WALL, 0, 0);
        return true;
    }
    return false;
}

void GinRummyGameState::DiscardCard(Card card)
{
    bool p1_discards = this->turn == GinTurn::P1_DISCARDS;
    bool p2_discards = this->turn == GinTurn::P2_DISCARDS;
    if (!p1_discards && !p2_discards)
        throw std::invalid_argument("Cannot discard: it is not the player's turn to discard");
    if (p1_discards)
    {
        if (this->cards_dealt + 1 != this->cards.player1_hand.size())
            throw std::invalid_argument("Cannot discard: player 1 has the wrong number of cards");
        // remove `card` from player 1's hand
        RemoveCard(this->cards.player1_hand, card);
    }
    if (p2_discards)
    {
        if (this->cards_dealt + 1 != this->cards.player2_hand.size())
            throw std::invalid_argument("Cannot discard: player 2 has the wrong number of cards");
        // remove `card` from player 2's hand
        RemoveCard(this->cards.player2_hand, card);
    }
    Cards hand = p1_discards ? this->cards.player1_hand : this->cards.player2_hand;
    int deadwood = this->GetDeadwood(hand);
    if (deadwood == 0)
    {
        // if player makes gin, the game ends
        Cards opp_hand = p1_discards ? this->cards.player2_hand : this->cards.player1_hand;
        int opp_deadwood = this->GetDeadwood(opp_hand);
        int p1_deadwood = p1_discards ? 0 : opp_deadwood;
        int p2_deadwood = p1_discards ? opp_deadwood : 0;
        GinEnding how = p1_discards ? GinEnding::P1_GINS : GinEnding::P2_GINS;
        this->EndGame(how, p1_deadwood, p2_deadwood);
    }
    else
        this->turn = this->AdvanceTurn(this->turn, false, deadwood);

    if (this->cards.discard_pile.size() > 0)
        this->public_hud[this->TopOfDiscard()] = GinHud::IN_DISCARD_PILE;
    this->public_hud[card] = GinHud::TOP_OF_DISCARD_PILE;
    this->cards.discard_pile.push_back(card);

    if (this->turn != GinTurn::P1_MAY_KNOCK || this->turn != GinTurn::P2_MAY_KNOCK)
    {
        // if they can't knock, then check if there are 2 cards left.
        // and if so, the game ends
        //
        // if not, we let them decide whether to knock,
        // and if they don't, it ends
        this->EndIfHitWall();
    }
};

void GinRummyGameState::DecideKnock(bool knocks, std::optional<Melds> melds)
{
    bool p1 = this->turn == GinTurn::P1_MAY_KNOCK;
    bool p2 = this->turn == GinTurn::P2_MAY_KNOCK;
    if (!p1 && !p2)
        throw std::invalid_argument("Cannot knock: it is not the player's turn to knock");
    if (!knocks)
    {
        // if they don't knock, check whether the game should end
        // based on whether we've hit the wall
        if (!this->EndIfHitWall())
            this->turn = this->AdvanceTurn(this->turn);
        return;
    }
    if (p1)
    {
        int p1_deadwood = this->GetDeadwood(this->cards.player1_hand, melds);
        int p2_deadwood = this->GetDeadwood(this->cards.player2_hand, std::nullopt, melds);
        this->EndGame(GinEnding::P1_KNOCKS, p1_deadwood, p2_deadwood);
    }
    else if (p2)
    {
        int p1_deadwood = this->GetDeadwood(this->cards.player1_hand, std::nullopt, melds);
        int p2_deadwood = this->GetDeadwood(this->cards.player2_hand, melds);
        this->EndGame(GinEnding::P2_KNOCKS, p1_deadwood, p2_deadwood);
    }
    else
        throw std::invalid_argument("invalid knocking state");
};

void GinRummyGameState::EndGame(GinEnding how, int p1_deadwood, int p2_deadwood)
{

    if (how == GinEnding::PLAYED_TO_THE_WALL)
    {
        this->p1_score = 0;
        this->p2_score = 0;
    }
    else if (how == GinEnding::P1_GINS)
    {
        this->p1_score = 0;
        this->p2_score = p2_deadwood + this->gin_bonus;
    }
    else if (how == GinEnding::P1_BIG_GINS)
    {
        this->p1_score = 0;
        this->p2_score = p2_deadwood + this->big_gin_bonus;
    }
    else if (how == GinEnding::P2_GINS)
    {
        this->p1_score = p1_deadwood + this->gin_bonus;
        this->p2_score = 0;
    }
    else if (how == GinEnding::P2_BIG_GINS)
    {
        this->p1_score = p1_deadwood + this->big_gin_bonus;
        this->p2_score = 0;
    }
    else if (how == GinEnding::P1_KNOCKS)
    {
        if (p2_deadwood <= p1_deadwood)
        {
            // p2 undercuts
            this->p1_score = p1_deadwood - p2_deadwood + this->undercut_bonus;
            this->p2_score = 0;
        }
        else
        {
            this->p1_score = 0;
            this->p2_score = p2_deadwood - p1_deadwood;
        }
    }
    else if (how == GinEnding::P2_KNOCKS)
    {
        if (p1_deadwood <= p2_deadwood)
        {
            // p1 undercuts
            this->p1_score = 0;
            this->p2_score = p2_deadwood - p1_deadwood + this->undercut_bonus;
        }
        else
        {
            this->p1_score = p1_deadwood - p2_deadwood;
            this->p2_score = 0;
        }
    }
};

void GinRummyGameState::AddToHand(bool p1, Card card)
{
    if (p1 && IsP1Draw(this->turn))
    {
        this->cards.player1_hand.push_back(card);
    }
    else if (!p1 && IsP2Draw(this->turn))
    {
        this->cards.player2_hand.push_back(card);
    }
    else
    {
        throw std::runtime_error("Cannot add to hand when it is not your turn to draw");
    }
};

Card GinRummyGameState::TopOfDiscard()
{
    // return the item at the top of the discard pile
    return this->cards.discard_pile.back();
};

Card GinRummyGameState::TopOfDeck()
{
    // return the item at the top of the deck
    return this->cards.deck.front();
};

CardsHud GinRummyGameState::PlayerHud(bool p1)
{
    CardsHud player_hud = {};
    for (const Card card : OrderedDeck())
    {
        // put all the cards in the deck
        player_hud[card] = GinHud::LIVE;
    }
    for (auto const &[card, hud] : this->public_hud)
    {
        if (hud == GinHud::TOP_OF_DISCARD_PILE || hud == GinHud::IN_DISCARD_PILE)
            player_hud[card] = hud;
        // it's publically known to be in our hand
        else if (p1 && hud == GinHud::PLAYER_1)
            player_hud[card] = GinHud::USER;
        else if (!p1 && hud == GinHud::PLAYER_2)
            player_hud[card] = GinHud::USER;
        // it's publically known to be in opponent's hand
        else if (p1 && hud == GinHud::PLAYER_2)
            player_hud[card] = GinHud::OPPONENT;
        else if (!p1 && hud == GinHud::PLAYER_1)
            player_hud[card] = GinHud::OPPONENT;
    }
    if (p1)
        for (const Card card : this->cards.player1_hand)
            player_hud[card] = GinHud::USER;
    else
        for (const Card card : this->cards.player2_hand)
            player_hud[card] = GinHud::USER;
    return player_hud;
};

GinTurn GinRummyGameState::AdvanceTurn(GinTurn current, bool from_discard, int deadwood)
{
    switch (current)
    {
    case GinTurn::P1_DRAWS_FIRST:
        if (from_discard)
            return GinTurn::P1_DISCARDS;
        else if (this->first_turn == GinTurn::P2_DRAWS_FIRST)
            return GinTurn::P2_DRAWS_FROM_DECK;
        else
            return GinTurn::P2_DRAWS_FIRST;
    case GinTurn::P2_DRAWS_FIRST:
        if (from_discard)
            return GinTurn::P2_DISCARDS;
        else if (this->first_turn == GinTurn::P1_DRAWS_FIRST)
            return GinTurn::P1_DRAWS_FROM_DECK;
        else
            return GinTurn::P1_DRAWS_FIRST;
    case GinTurn::P1_DRAWS_FROM_DECK:
        return GinTurn::P1_DISCARDS;
    case GinTurn::P2_DRAWS_FROM_DECK:
        return GinTurn::P2_DISCARDS;
    case GinTurn::P1_DRAWS:
        return GinTurn::P1_DISCARDS;
    case GinTurn::P1_DISCARDS:
        if (deadwood <= 10)
            return GinTurn::P1_MAY_KNOCK;
        else
            return GinTurn::P2_DRAWS;
    case GinTurn::P1_MAY_KNOCK:
        return GinTurn::P2_DRAWS;
    case GinTurn::P2_DRAWS:
        return GinTurn::P2_DISCARDS;
    case GinTurn::P2_DISCARDS:
        if (deadwood <= 10)
            return GinTurn::P2_MAY_KNOCK;
        else
            return GinTurn::P1_DRAWS;
    case GinTurn::P2_MAY_KNOCK:
        return GinTurn::P1_DRAWS;
    default:
        throw std::runtime_error("Invalid turn");
    }
}

int GinRummyGameState::GetDeadwood(const Cards hand, std::optional<Melds> melds, std::optional<Melds> opp_melds)
{
    if (opp_melds.has_value())
    {
        auto lo = LayoffDeadwood(hand, opp_melds.value());
        return std::get<0>(lo);
    }
    SplitHand split_melds = SplitMelds(hand, melds);
    return std::get<0>(split_melds);
};

Cards GinRummyGameState::SortHand(Cards hand)
{
    SplitHand split_melds = SplitMelds(hand);
    std::vector<Cards> melds = std::get<1>(split_melds);
    Cards unmelded = std::get<2>(split_melds);

    Cards sorted_hand = {};
    for (const Cards meld : melds)
    {
        sorted_hand.insert(sorted_hand.end(), meld.begin(), meld.end());
    }
    sorted_hand.insert(sorted_hand.end(), unmelded.begin(), unmelded.end());
    return sorted_hand;
};

static bool random_bool()
{
    std::random_device rd;                 // Initialize a random device
    std::mt19937 gen(rd());                // Initialize a Mersenne Twister pseudorandom generator with the random device
    std::bernoulli_distribution dist(0.5); // Initialize a Bernoulli distribution that gives 1 with a probability of 0.5
    return dist(gen);                      // Return a random boolean
}

GinRummyGameState NewGinRummyGame()
{

    bool p1_first = random_bool();
    GinTurn first_turn = p1_first ? GinTurn::P1_DRAWS_FIRST : GinTurn::P2_DRAWS_FIRST;
    GinTurn turn = first_turn;
    GinCards cards = DealHands(10);
    return GinRummyGameState(cards, turn, first_turn);
}