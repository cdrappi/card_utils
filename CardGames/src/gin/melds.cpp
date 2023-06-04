// melds.cpp

#include <algorithm>
#include <map>
#include <tuple>

#include "melds.hpp"
#include "gin_rummy.hpp"
#include "../deck/card.hpp"
#include "../deck/rank.hpp"
#include "../deck/suit.hpp"

std::map<Rank, std::vector<Suit>> RankPartition(const std::vector<Card> &cards)
{
    std::map<Rank, std::vector<Suit>> rankToSuitsMap;

    // Group the cards by rank
    for (const auto &card : cards)
    {
        rankToSuitsMap[card.rank].push_back(card.suit);
    }

    return rankToSuitsMap;
}

std::map<Suit, std::vector<Rank>> SuitPartition(const std::vector<Card> &cards)
{
    std::map<Suit, std::vector<Rank>> suitToRanksMap;

    // Group the cards by suit
    for (const auto &card : cards)
    {
        suitToRanksMap[card.suit].push_back(card.rank);
    }

    return suitToRanksMap;
}

static Melds FindSets(const std::vector<Card> &cards)
{
    const auto rankToSuitsMap = RankPartition(cards);

    Melds sets;

    // Iterate over each rank
    for (const auto &[rank, suits] : rankToSuitsMap)
    {

        // If there are 3 or more cards of the same rank, add them to setsOfThree
        if (suits.size() == 3)
        {
            CardSet cards;
            for (const auto &suit : suits)
            {
                Card card = Card(rank, suit);
                cards.insert(card);
            }
            sets.push_back(std::move(cards));
        }

        // If there are 4 or more cards of the same rank:
        // -> add them to setsOfFour
        // -> add all possible combinations of 3 cards to setsOfThree
        if (suits.size() == 4)
        {
            // add to sets of four
            CardSet cards;
            for (const auto &suit : suits)
            {
                cards.insert(Card(rank, suit));
            }
            sets.push_back(std::move(cards));

            // add all possible combinations of 3 cards to sets of three
            for (const auto &exclude_suit : suits)
            {
                CardSet cards;
                for (const auto &suit : suits)
                {
                    if (suit != exclude_suit)
                    {
                        cards.insert(Card(rank, suit));
                    }
                }
                sets.push_back(std::move(cards));
            }
        }
    }

    return sets;
}

static RankValues SortedRankValues(const Ranks &ranks, bool aces_low, bool aces_high)
{
    RankValues values;

    for (const auto &rank : ranks)
    {
        if (rank == ACE)
        {
            if (aces_low)
            {
                values.push_back(static_cast<int>(rank));
            }
            if (aces_high)
            {
                values.push_back(static_cast<int>(KING) + 1);
            }
        }
        else
        {
            values.push_back(static_cast<int>(rank));
        }
    }

    std::sort(values.begin(), values.end());
    return values;
}

static std::vector<RankValues> SplitConnectedValues(const RankValues &sorted_values)
{
    std::vector<RankValues> connected_values;

    int last_value = sorted_values[0];

    RankValues current_values;
    current_values.push_back(last_value);

    for (int i = 1; i < sorted_values.size(); ++i)
    {
        int value = sorted_values[i];
        if (value == last_value + 1)
        // they are connected, so add to the current group
        {
            current_values.push_back(value);
        }
        else
        // they are not, so start a new group
        {
            {
                connected_values.push_back(current_values);
                current_values.clear();
                current_values.push_back(value);
            }
        }
        last_value = value;
    }

    if (!current_values.empty())
    {
        connected_values.push_back(current_values);
    }

    return connected_values;
}

static std::vector<RankValues> FindStraightCombinations(const RankValues &connected_values, int min_length, int max_length)
{
    std::vector<RankValues> straight_combinations;

    int n = connected_values.size();
    int max_len = std::min(n, max_length);
    for (int size = min_length; size <= max_len; ++size)
    {
        for (int i = 0; i <= n - size; ++i)
        {
            RankValues straight;
            for (int j = 0; j < size; ++j)
            {
                straight.push_back(connected_values[i + j]);
            }
            straight_combinations.push_back(straight);
        }
    }
    return straight_combinations;
}

/*
given a list of ranks (all with the same suit),
find all possible straights of length min_length to max_length
*/
static std::vector<Ranks> FindStraights(const Ranks &ranks,
                                        int min_length = 3,
                                        int max_length = 13,
                                        bool aces_low = true,
                                        bool aces_high = true)
{

    if (ranks.size() < min_length)
        return {};

    if (!aces_high && !aces_low)
        throw std::invalid_argument("At least one of aces_low or aces_high must be true");

    // sort the ranks
    RankValues values = SortedRankValues(ranks, aces_low, aces_high);
    std::vector<RankValues> connected_values = SplitConnectedValues(values);

    std::vector<Ranks> straights;
    for (int i = 0; i < connected_values.size(); i++)
    {
        std::vector<RankValues> straight_combinations = FindStraightCombinations(connected_values[i], min_length, max_length);
        for (int j = 0; j < straight_combinations.size(); j++)
        {
            Ranks straight;
            for (int k = 0; k < straight_combinations[j].size(); k++)
            {
                straight.push_back(ValueToRank(straight_combinations[j][k]));
            }
            straights.push_back(straight);
        }
    }

    return straights;
}

static Melds FindRuns(const std::vector<Card> &cards)
{
    const auto suitPartition = SuitPartition(cards);
    Melds runs;

    for (const auto &[suit, ranks] : suitPartition)
    {
        const auto straights = FindStraights(ranks);
        for (const auto &straight : straights)
        {
            CardSet run;
            for (const auto &rank : straight)
            {
                run.insert(Card(rank, suit));
            }
            if (run.size() > 0)
                runs.push_back(run);
        }
    }
    return runs;
}

static CardSet CardsToSet(const Cards &cards)
{
    return CardSet(cards.begin(), cards.end());
}

static CardSet MeldsToSet(const Melds &melds)
{
    CardSet melded_cards;
    for (const auto &meld : melds)
    {
        melded_cards.insert(meld.begin(), meld.end());
    }
    return melded_cards;
}

static Cards UnmeldedCards(const Cards &hand, const Melds &melds)
{
    CardSet hand_set = CardsToSet(hand);
    CardSet melded_cards = MeldsToSet(melds);
    CardSet unmelded_cards;
    std::set_difference(
        hand_set.begin(),
        hand_set.end(),
        melded_cards.begin(),
        melded_cards.end(),
        std::inserter(unmelded_cards, unmelded_cards.begin()));
    return Cards(unmelded_cards.begin(), unmelded_cards.end());
}

static Melds FindMelds(const Cards &hand)
{
    Melds melds = FindSets(hand);
    Melds runs = FindRuns(hand);
    melds.insert(melds.end(), runs.begin(), runs.end());
    return melds;
}

static std::vector<Melds> MeldCombinations(Melds &v, int r)
{

    if (r > v.size())
        return {};

    std::vector<bool> vMask(v.size());
    std::fill(vMask.begin(), vMask.begin() + r, true);

    std::vector<Melds> combinations;
    do
    {
        std::vector<CardSet> vComb;
        for (int i = 0; i < v.size(); ++i)
        {
            if (vMask[i])
                vComb.push_back(v[i]);
        }
        combinations.push_back(vComb);
    } while (std::prev_permutation(vMask.begin(), vMask.end()));

    return combinations;
}

static std::vector<Cards> SortMelds(const Melds &melds)
{
    std::vector<Cards> sorted_melds;
    for (const auto &meld : melds)
    {
        Cards sorted_meld(meld.begin(), meld.end());
        std::sort(sorted_meld.begin(), sorted_meld.end());
        if (sorted_meld[0].rank == ACE && sorted_meld[sorted_meld.size() - 1].rank == KING)
        {
            // move the ace to the back of the vector
            std::rotate(sorted_meld.begin(), sorted_meld.begin() + 1, sorted_meld.end());
        }
        sorted_melds.push_back(sorted_meld);
    }

    return sorted_melds;
}

std::vector<SplitHand> GetCandidateMelds(
    const Cards &hand,
    std::optional<int> max_deadwood, // = std::nullopt,
    bool stop_on_gin)                // = true)
{
    std::vector<SplitHand> candidate_melds;

    int full_deadwood = GinRummyCardsDeadwood(hand);
    if (!max_deadwood.has_value() || full_deadwood <= max_deadwood.value())
    {
        candidate_melds.push_back({full_deadwood, {}, hand});
    }

    Melds all_melds = FindMelds(hand);
    int n_melds = all_melds.size();
    for (int n_combos = 1; n_combos <= std::min(3, n_melds); n_combos++)
    {
        std::vector<Melds> meld_combos = MeldCombinations(all_melds, n_combos);
        for (int i = 0; i < meld_combos.size(); i++)
        {
            Melds meld_combo = meld_combos[i];
            CardSet melded_cards = MeldsToSet(meld_combo);
            int melds_size = 0;
            for (int j = 0; j < meld_combo.size(); j++)
            {
                melds_size += meld_combo[j].size();
            }
            if (melded_cards.size() == melds_size)
            {
                Cards unmelded_cards = UnmeldedCards(hand, meld_combo);
                if (stop_on_gin && unmelded_cards.size() == 0)
                {
                    return {SplitHand{0, SortMelds(meld_combo), {}}};
                }
                int deadwood = GinRummyCardsDeadwood(unmelded_cards);
                if (!max_deadwood.has_value() || deadwood <= max_deadwood.value())
                {
                    SortByRank(unmelded_cards);
                    candidate_melds.push_back({deadwood, SortMelds(meld_combo), unmelded_cards});
                }
            }
        }
    }

    return candidate_melds;
}

SplitHand SplitMelds(const Cards &hand, std::optional<Melds> melds)
{
    if (melds.has_value())
    {
        Melds chosen_melds = melds.value();
        Cards unmelded = UnmeldedCards(hand, chosen_melds);
        int deadwood = GinRummyCardsDeadwood(unmelded);
        return {deadwood, SortMelds(chosen_melds), unmelded};
    }

    auto candidate_melds = GetCandidateMelds(hand);
    auto split_hand = std::min_element(
        candidate_melds.begin(),
        candidate_melds.end(),
        // pick the meld combo with the least deadwood
        [](const SplitHand &a, const SplitHand &b)
        { return std::get<0>(a) < std::get<0>(b); });

    return *split_hand;
}