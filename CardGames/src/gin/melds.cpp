// melds.cpp

#include <algorithm>
#include <map>
#include <tuple>
#include <vector>
#include <iostream>
#include <unordered_map>

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
        rankToSuitsMap[card.rank].push_back(card.suit);

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
        if (rank == Rank::ACE)
        {
            if (aces_low)
                values.push_back(static_cast<int>(rank));
            if (aces_high)
                values.push_back(static_cast<int>(Rank::KING) + 1);
        }
        else
            values.push_back(static_cast<int>(rank));
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
    // first order the melds by size
    Melds melds_copy = melds;
    std::sort(
        melds_copy.begin(),
        melds_copy.end(),
        [](const CardSet a, const CardSet b)
        { return a.size() > b.size(); });

    std::vector<Cards> sorted_melds;
    for (const auto &meld : melds_copy)
    {
        Cards sorted_meld(meld.begin(), meld.end());
        std::sort(sorted_meld.begin(), sorted_meld.end());
        if (sorted_meld[0].rank == Rank::ACE && sorted_meld[sorted_meld.size() - 1].rank == Rank::KING)
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
        Cards hand_copy = hand;
        SortByRank(hand_copy);
        candidate_melds.push_back({full_deadwood, {}, hand_copy});
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

SplitHand SplitMelds(const Cards &hand, const std::optional<Melds> &melds)
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

#include <vector>
#include <iostream>

template <typename T>
std::vector<std::vector<T>> Powerset(const std::vector<T> &set, int index)
{
    std::vector<std::vector<T>> subsets;
    if (index == set.size())
    {
        // Base case: add an empty set
        subsets.push_back({});
    }
    else
    {
        // Recursive case
        subsets = Powerset(set, index + 1);
        int subsetsSize = subsets.size();
        for (int i = 0; i < subsetsSize; i++)
        {
            // create a new subset from the existing subsets and add the current element to it
            std::vector<T> newSubset = subsets[i];
            newSubset.push_back(set[index]);
            subsets.push_back(newSubset);
        }
    }
    return subsets;
}

std::tuple<std::vector<Rank>, std::unordered_map<Suit, std::vector<std::pair<Rank, Rank>>>>
SplitSetsRuns(const Melds &melds)
{
    std::vector<Rank> sets;
    std::unordered_map<Suit, std::vector<std::pair<Rank, Rank>>> runs;

    for (auto &meld : melds)
    {
        auto meld_vec = std::vector<Card>(meld.begin(), meld.end());
        auto sp = SuitPartition(meld_vec);
        auto rp = RankPartition(meld_vec);
        if (sp.size() == 1)
        {
            auto [suit, ranks] = *sp.begin();
            if (runs.count(suit) == 0)
            {
                runs[suit] = {};
            }
            runs[suit].push_back({ranks.front(), ranks.back()});
        }
        else if (rp.size() == 1)
        {
            auto [rank, suits] = *rp.begin();
            if (suits.size() == 3)
            {
                // 4-sets can't be laid off against, so only consider 3-sets
                sets.push_back(rank);
            }
        }
        else
        {
            throw std::invalid_argument("Invalid meld passed into SplitSetsRuns");
        }
    }

    return {sets, runs};
}

Cards GetSetLayoffs(const Cards &hand, const std::vector<Rank> &sets)
{
    Cards result;
    auto rp = RankPartition(hand);

    for (const auto &r : sets)
    {
        if (rp.count(r) > 0)
            result.push_back(Card(r, rp[r][0]));
    }
    return result;
}

std::optional<Rank> NextLowRank(int low_value)
{
    std::optional<Rank> next_low = std::nullopt;
    if (low_value > int(Rank::ACE))
        next_low = ValueToRank(low_value - 1);
    return next_low;
}

std::optional<Rank> NextHighRank(int high_value)
{
    std::optional<Rank> next_high = std::nullopt;
    if (high_value < int(Rank::KING) + 1)
    {
        next_high = ValueToRank(high_value + 1);
    }
    return next_high;
}

std::vector<Ranks> GetSuitRunLayoffs(
    const Ranks &suit_ranks,
    const std::vector<std::pair<Rank, Rank>> &suit_runs)
{

    if (suit_ranks.empty())
        return {};

    std::set<Rank> rank_set(suit_ranks.begin(), suit_ranks.end());
    std::vector<Ranks> layoff_ranks;
    for (auto const &[low, high] : suit_runs)
    {
        int low_value = int(low);
        int high_value = high != Rank::ACE ? int(high) : int(Rank::KING) + 1;
        std::optional<Rank> next_low = NextLowRank(low_value);
        std::optional<Rank> next_high = NextHighRank(high_value);

        Ranks laid_off_low;
        while (next_low.has_value() && rank_set.count(next_low.value()))
        {
            rank_set.erase(next_low.value());
            laid_off_low.push_back(next_low.value());
            low_value -= 1;
            next_low = NextLowRank(low_value);
        }
        if (!laid_off_low.empty())
            layoff_ranks.push_back(laid_off_low);

        Ranks laid_off_high;
        while (next_high.has_value() && rank_set.count(next_high.value()))
        {
            rank_set.erase(next_high.value());
            laid_off_high.push_back(next_high.value());
            high_value += 1;
            next_high = NextHighRank(high_value);
        }
        if (!laid_off_high.empty())
            layoff_ranks.push_back(laid_off_high);
    }
    return layoff_ranks;
}

std::vector<Cards> GetRunLayoffs(
    const Cards &hand,
    const std::unordered_map<Suit, std::vector<std::pair<Rank, Rank>>> &runs)
{

    auto sp = SuitPartition(hand);
    std::vector<Cards> layoff_card_chunks;

    for (auto const &[suit, suit_runs] : runs)
    {
        auto suit_chunks = GetSuitRunLayoffs(sp[suit], suit_runs);
        for (auto const &sc : suit_chunks)
        {
            std::vector<Card> card_chunk;
            for (auto const &r : sc)
            {
                card_chunk.push_back(Card(r, suit));
            }
            layoff_card_chunks.push_back(card_chunk);
        }
    }
    return layoff_card_chunks;
}

std::tuple<int, std::vector<Cards>, Cards, Cards>
LayoffDeadwood(
    const Cards &hand,
    const Melds &opp_melds,
    bool stop_on_zero)
{
    auto [sets, runs] = SplitSetsRuns(opp_melds);
    std::vector<std::tuple<int, std::vector<Cards>, Cards, Cards>> candidates;

    for (auto &[_, melds, unmelded] : GetCandidateMelds(hand))
    {
        // loop over each possible meld we can make,
        // and see what we can do with the remaining cards
        CardSet unmelded_set = CardsToSet(unmelded);
        Cards sls = GetSetLayoffs(unmelded, sets);
        for (auto &set_layoffs : Powerset(sls))
        {
            CardSet lo_sets = CardsToSet(set_layoffs);
            CardSet um_set;
            std::set_difference(unmelded_set.begin(), unmelded_set.end(), lo_sets.begin(), lo_sets.end(), std::inserter(um_set, um_set.end()));
            std::vector<Cards> rls = GetRunLayoffs(std::vector<Card>(um_set.begin(), um_set.end()), runs);
            for (auto &run_layoffs : Powerset(rls))
            {
                CardSet lo_runs;
                for (auto &rl : run_layoffs)
                    for (auto &c : rl)
                        lo_runs.insert(c);
                CardSet um_run;
                std::set_difference(um_set.begin(), um_set.end(), lo_runs.begin(), lo_runs.end(), std::inserter(um_run, um_run.end()));
                int deadwood = GinRummyCardsDeadwood(Cards(um_run.begin(), um_run.end()));
                Cards um_cards = Cards(um_run.begin(), um_run.end());
                CardSet laid_off_cards;
                std::set_union(lo_sets.begin(), lo_sets.end(), lo_runs.begin(), lo_runs.end(), std::inserter(laid_off_cards, laid_off_cards.end()));
                auto candidate = std::make_tuple(
                    deadwood,
                    melds,
                    Cards(laid_off_cards.begin(), laid_off_cards.end()),
                    um_cards);
                if (stop_on_zero && deadwood == 0)
                    return candidate;
                candidates.push_back(candidate);
            }
        }
    }
    return *std::min_element(
        candidates.begin(),
        candidates.end(),
        [](auto const &a, auto const &b)
        { return std::get<0>(a) < std::get<0>(b); });
    return {0, {}, {}, {}};
}