// melds.cpp

#include "melds.hpp"
#include "gin_rummy.hpp"
#include "../deck/card.hpp"
#include "../deck/rank.hpp"
#include "../deck/suit.hpp"

std::array<std::vector<Suit>, 13> RankPartition(const std::vector<Card> &cards)
{
    // auto start = std::chrono::high_resolution_clock::now();
    std::array<std::vector<Suit>, 13> rankToSuitsMap;

    // Group the cards by rank
    for (const auto &card : cards)
    {
        int rank_int = int(card.rank);
        if (rankToSuitsMap[rank_int].size() == 0)
        {
            rankToSuitsMap[rank_int].reserve(4);
        }
        rankToSuitsMap[rank_int].push_back(card.suit);
    }

    // auto end = std::chrono::high_resolution_clock::now();
    // std::cout << "RankPartition took "
    //           << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()
    //           << " microseconds\n";

    return rankToSuitsMap;
}

std::array<std::vector<Rank>, 4> SuitPartition(const std::vector<Card> &cards)
{
    // auto start = std::chrono::high_resolution_clock::now();
    std::array<std::vector<Rank>, 4> suitToRanksMap;

    // Group the cards by suit
    for (const auto &card : cards)
    {
        int suit_int = int(card.suit);
        if (suitToRanksMap[suit_int].size() == 0)
            suitToRanksMap[suit_int].reserve(13);
        suitToRanksMap[suit_int].push_back(card.rank);
    }

    // for (auto &[suit, ranks] : suitToRanksMap)
    //     std::sort(ranks.begin(), ranks.end());
    // auto end = std::chrono::high_resolution_clock::now();
    // std::cout << "SuitPartition took "
    //           << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()
    //           << " microseconds\n";

    return suitToRanksMap;
}

static Melds FindSets(const std::vector<Card> &cards)
{

    const auto rankToSuitsMap = RankPartition(cards);

    Melds sets;

    // Iterate over each rank
    for (Rank rank : ALL_RANKS)
    {
        std::vector<Suit> suits = rankToSuitsMap[int(rank)];
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

    // auto end = std::chrono::high_resolution_clock::now();
    // std::cout << "FindSets took "
    //           << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()
    //           << " microseconds\n";

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
    if (cards.size() < 3)
        return {};

    // auto start = std::chrono::high_resolution_clock::now();

    const auto suitPartition = SuitPartition(cards);
    Melds runs;

    for (Suit suit : ALL_SUITS)
    {
        std::vector<Rank> ranks = suitPartition[int(suit)];
        const auto straights = FindStraights(ranks);
        for (const auto &straight : straights)
        {
            CardSet run;
            for (const auto &rank : straight)
                run.insert(Card(rank, suit));

            if (run.size() > 0)
                runs.push_back(run);
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    // std::cout << "C++ FindRuns took "
    //           << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()
    //           << " microseconds\n";

    return runs;
}

static CardSet CardsToSet(const Cards &cards)
{
    return CardSet(cards.begin(), cards.end());
}

static SortedCardSet CardsToSortedSet(const Cards &cards)
{
    return SortedCardSet(cards.begin(), cards.end());
}

static CardSet MeldsToSet(const Melds &melds)
{
    CardSet melded_cards;
    for (const auto &meld : melds)
        melded_cards.insert(meld.begin(), meld.end());

    return melded_cards;
}

static SortedCardSet MeldsToSortedSet(const Melds &melds)
{
    SortedCardSet melded_cards;
    for (const auto &meld : melds)
        melded_cards.insert(meld.begin(), meld.end());

    return melded_cards;
}

static Cards UnmeldedCards(const SortedCardSet &hand_set, const SortedCardSet &melded_cards)
{
    SortedCardSet unmelded_cards;
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

bool AddUniqueCards(CardSet &cards1, const CardSet &cards2)
{
    for (const auto &card : cards2)
    {
        if (cards1.find(card) != cards1.end())
            return false;
        else
            cards1.insert(card);
    }
    return true;
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
        CardSet cards_in_meld = {};
        std::vector<CardSet> vComb;
        for (int i = 0; i < v.size(); ++i)
        {
            if (vMask[i])
            {
                if (AddUniqueCards(cards_in_meld, v[i]))
                {
                    vComb.push_back(v[i]);
                }
                else
                {
                    vComb.clear();
                    break;
                }
            }
        }
        combinations.push_back(vComb);
    } while (std::prev_permutation(vMask.begin(), vMask.end()));

    return combinations;
}

std::vector<Cards> SortMelds(const Melds &melds)
{
    if (melds.size() == 0)
        return {};

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
        // SortByRank(hand_copy);
        candidate_melds.push_back({full_deadwood, {}, hand_copy});
    }

    SortedCardSet hand_set = CardsToSortedSet(hand);

    // auto start = std::chrono::high_resolution_clock::now();
    Melds all_melds = FindMelds(hand);
    // auto end = std::chrono::high_resolution_clock::now();
    // std::cout << "C++ FindMelds took "
    //           << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()
    //           << " microseconds\n";
    int n_melds = all_melds.size();
    // std::cout << "n_melds " << n_melds << std::endl;

    // int total_combos = 0;
    for (int n_combos = 1; n_combos <= std::min(3, n_melds); n_combos++)
    {
        // auto start = std::chrono::high_resolution_clock::now();
        std::vector<Melds> meld_combos = MeldCombinations(all_melds, n_combos);
        // auto end = std::chrono::high_resolution_clock::now();
        // std::cout << "C++ MeldCombinations took "
        //           << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()
        //           << " microseconds\n";
        for (int i = 0; i < meld_combos.size(); i++)
        {
            // total_combos++;
            Melds meld_combo = meld_combos[i];
            SortedCardSet melded_cards = MeldsToSortedSet(meld_combo);

            // int melds_size = 0;
            // for (int j = 0; j < meld_combo.size(); j++)
            //     melds_size += meld_combo[j].size();

            if (true) // melded_cards.size() == melds_size)
            {
                Cards unmelded_cards = UnmeldedCards(hand_set, melded_cards);
                if (stop_on_gin && unmelded_cards.size() == 0)
                {
                    // std::cout << "C++ looped over " << total_combos << " combos" << std::endl;
                    return {SplitHand{0, meld_combo, {}}};
                }
                int deadwood = GinRummyCardsDeadwood(unmelded_cards);
                if (!max_deadwood.has_value() || deadwood <= max_deadwood.value())
                {
                    // SortByRank(unmelded_cards);
                    candidate_melds.push_back({deadwood, meld_combo, unmelded_cards});
                }
            }
        }
        // end = std::chrono::high_resolution_clock::now();
        // std::cout << "C++ MeldCombinations loop " << n_combos << " took " << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count() << " microseconds\n";
    }
    // std::cout << "C++ looped over " << total_combos << " combos" << std::endl;

    return candidate_melds;
}

SortedSplitHand SplitMelds(const Cards &hand, const std::optional<Melds> &melds)
{

    if (melds.has_value())
    {
        Melds chosen_melds = melds.value();
        Cards unmelded = UnmeldedCards(CardsToSortedSet(hand), MeldsToSortedSet(chosen_melds));
        int deadwood = GinRummyCardsDeadwood(unmelded);
        return {deadwood, SortMelds(chosen_melds), unmelded};
    }

    int start_result = ProfilerStart("split_melds.prof");
    auto candidate_melds = GetCandidateMelds(hand);
    for (int i = 0; i < 10'000; i++)
        candidate_melds = GetCandidateMelds(hand);

    auto split_hand = std::min_element(
        candidate_melds.begin(),
        candidate_melds.end(),
        // pick the meld combo with the least deadwood
        [](const SplitHand &a, const SplitHand &b)
        { return std::get<0>(a) < std::get<0>(b); });
    ProfilerStop();

    // auto end = std::chrono::high_resolution_clock::now();
    // std::cout << "C++ SplitMelds took "
    //           << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()
    //           << " micros" << std::endl;
    int deadwood = std::get<0>(*split_hand);
    Melds chosen_melds = std::get<1>(*split_hand);
    Cards unmelded = std::get<2>(*split_hand);
    SortByRank(unmelded);
    return SortedSplitHand{deadwood, SortMelds(chosen_melds), unmelded};
}

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

bool IsRun(const CardSet &meld)
{
    std::unordered_set<Suit> suits;
    std::unordered_set<Rank> ranks;
    for (auto &card : meld)
    {
        suits.insert(card.suit);
        ranks.insert(card.rank);
    }
    if (suits.size() == 1)
        return true;
    else if (ranks.size() == 1)
        return false;
    else
    {
        throw std::invalid_argument("Invalid meld passed into IsRun");
    }
}

std::tuple<std::vector<Rank>, std::unordered_map<Suit, std::vector<std::pair<Rank, Rank>>>>
SplitSetsRuns(const Melds &melds)
{
    std::vector<Rank> sets;
    std::unordered_map<Suit, std::vector<std::pair<Rank, Rank>>> runs;

    for (auto &meld : melds)
    {
        auto meld_vec = std::vector<Card>(meld.begin(), meld.end());
        if (IsRun(meld))
        {
            SortByRank(meld_vec);
            Card first = meld_vec.front();
            Card last = meld_vec.back();
            runs[first.suit].push_back({first.rank, last.rank});
        }
        else if (meld_vec.size() == 3)
            sets.push_back(meld_vec.front().rank);
    }

    return {sets, runs};
}

Cards GetSetLayoffs(const Cards &hand, const std::vector<Rank> &sets)
{
    Cards result;
    auto rp = RankPartition(hand);

    for (const auto &r : sets)
        if (rp[int(r)].size() > 0)
            result.push_back(Card(r, rp[int(r)][0]));
    return result;
}

std::optional<Rank> NextLowRank(int low_value)
{
    std::optional<Rank> next_low = std::nullopt;
    if (low_value <= int(Rank::ACE))
        return std::nullopt;
    return ValueToRank(low_value - 1);
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

    std::unordered_set<Rank> rank_set(suit_ranks.begin(), suit_ranks.end());
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
        auto suit_chunks = GetSuitRunLayoffs(sp[int(suit)], suit_runs);
        for (auto const &sc : suit_chunks)
        {
            std::vector<Card> card_chunk;
            for (auto const &r : sc)
                card_chunk.push_back(Card(r, suit));

            layoff_card_chunks.push_back(card_chunk);
        }
    }
    return layoff_card_chunks;
}

std::tuple<int, std::vector<Cards>, Cards, Cards> SortLayoffCandidate(
    std::tuple<int, Melds, Cards, Cards> candidate)
{
    int deadwood = std::get<0>(candidate);
    auto melds = std::get<1>(candidate);
    Cards layoffs = std::get<2>(candidate);
    Cards unmelded = std::get<3>(candidate);
    return {deadwood, SortMelds(melds), layoffs, unmelded};
}

std::tuple<int, std::vector<Cards>, Cards, Cards>
LayoffDeadwood(
    const Cards &hand,
    const Melds &opp_melds,
    bool stop_on_zero)
{
    auto [sets, runs] = SplitSetsRuns(opp_melds);
    std::vector<std::tuple<int, Melds, Cards, Cards>> candidates;

    for (auto &[_, melds, unmelded] : GetCandidateMelds(hand))
    {
        // loop over each possible meld we can make,
        // and see what we can do with the remaining cards
        CardSet unmelded_set = CardsToSet(unmelded);
        Cards sls = GetSetLayoffs(unmelded, sets);
        for (auto &set_layoffs : Powerset(sls))
        {
            SortedCardSet lo_sets = CardsToSortedSet(set_layoffs);
            SortedCardSet um_set;
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
                    return SortLayoffCandidate(candidate);
                candidates.push_back(candidate);
            }
        }
    }

    auto best_candidate = *std::min_element(
        candidates.begin(),
        candidates.end(),
        [](auto const &a, auto const &b)
        { return std::get<0>(a) < std::get<0>(b); });
    return SortLayoffCandidate(best_candidate);
}