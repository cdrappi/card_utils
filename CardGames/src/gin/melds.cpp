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
            Cards cards;
            cards.reserve(3);
            for (const auto &suit : suits)
            {
                cards.push_back(Card(rank, suit));
            }
            sets.push_back(std::move(cards));
        }

        // If there are 4 or more cards of the same rank:
        // -> add them to setsOfFour
        // -> add all possible combinations of 3 cards to setsOfThree
        if (suits.size() == 4)
        {
            // add to sets of four
            Cards cards;
            cards.reserve(4);
            for (const auto &suit : suits)
            {
                cards.push_back(Card(rank, suit));
            }
            sets.push_back(std::move(cards));

            // add all possible combinations of 3 cards to sets of three
            for (const auto &exclude_suit : suits)
            {
                Cards cards;
                cards.reserve(3);
                for (const auto &suit : suits)
                {
                    if (suit != exclude_suit)
                    {
                        cards.push_back(Card(rank, suit));
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
    // can have up to 4 aces
    values.reserve(ranks.size() + 4 * (int(aces_high) + int(aces_low) - 1));

    for (const auto &rank : ranks)
    {
        if (rank == Rank::ACE)
        {
            if (aces_low)
                values.push_back(int(rank));
            if (aces_high)
                values.push_back(int(Rank::KING) + 1);
        }
        else
            values.push_back(int(rank));
    }

    std::sort(values.begin(), values.end());
    return values;
}

static std::vector<RankValues> SplitConnectedValues(const RankValues &sorted_values)
{
    std::vector<RankValues> connected_values;

    int max_size = std::min(7, int(sorted_values.size()));
    connected_values.reserve(max_size);

    int last_value = sorted_values[0];

    RankValues current_values;
    current_values.reserve(max_size);
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
                connected_values.push_back(std::move(current_values));
                current_values = {value};
                current_values.reserve(max_size);
            }
        }
        last_value = value;
    }

    if (!current_values.empty())
    {
        connected_values.push_back(std::move(current_values));
    }

    return connected_values;
}

static std::vector<RankValues> FindStraightCombinations(const RankValues &connected_values, int min_length, int max_length)
{

    int n = connected_values.size();
    int max_len = std::min(n, max_length);

    std::vector<RankValues> straight_combinations;
    // TODO: reserve?
    for (int size = min_length; size <= max_len; ++size)
    {
        for (int i = 0; i <= n - size; ++i)
        {
            RankValues straight;
            straight.reserve(size);
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
            straight.reserve(straight_combinations[j].size());
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
            if (int straight_size = straight.size() > 0)
            {
                Cards run;
                run.reserve(straight_size);
                for (const auto &rank : straight)
                    run.push_back(Card(rank, suit));
                runs.push_back(run);
            }
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

static SortedCardSet MeldsToSortedSet(const Melds &melds)
{
    SortedCardSet melded_cards;
    for (const auto &meld : melds)
        melded_cards.insert(meld.begin(), meld.end());

    return melded_cards;
}

static Cards UnmeldedCards(const Cards &hand, const CardIds &melded_card_ids)
{
    Cards unmelded_cards;
    unmelded_cards.reserve(hand.size());
    for (const auto &card : hand)
    {
        if (melded_card_ids[card.ToId()] == 0)
            unmelded_cards.push_back(card);
    }

    return unmelded_cards;
}

static Melds FindMelds(const Cards &hand)
{
    Melds melds = FindSets(hand);
    Melds runs = FindRuns(hand);
    melds.insert(melds.end(), runs.begin(), runs.end());
    return melds;
}

bool AddUniqueCards(CardIds &add_to, const Cards &add_from, int meld_n)
{
    for (const auto &card : add_from)
    {
        int card_id = card.ToId();
        if (add_to[card_id] != 0)
            return false;
        else
            add_to[card_id] = meld_n;
    }
    return true;
}

static std::vector<CardIds> MeldCombinations(Melds &v, int r)
{

    if (r > v.size())
        return {};

    std::vector<bool> vMask(v.size());
    std::fill(vMask.begin(), vMask.begin() + r, true);

    std::vector<CardIds> combinations;
    do
    {
        CardIds cards_in_meld;
        cards_in_meld.fill(0);

        bool unique_cards = true;
        int meld_n = 0;
        for (int i = 0; i < v.size(); ++i)
        {
            if (vMask[i])
            {
                meld_n += 1;
                if (!AddUniqueCards(cards_in_meld, v[i], meld_n))
                {
                    unique_cards = false;
                    break;
                }
            }
        }
        if (unique_cards)
            combinations.push_back(std::move(cards_in_meld));
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
        [](const Cards a, const Cards b)
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
        CardIds melded_card_ids;
        melded_card_ids.fill(0);
        SplitHand full_deadwood_hand = std::make_tuple(full_deadwood, melded_card_ids, hand_copy);
        candidate_melds.push_back(std::move(full_deadwood_hand));
    }

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
        std::vector<CardIds> meld_combos = MeldCombinations(all_melds, n_combos);
        // auto end = std::chrono::high_resolution_clock::now();
        // std::cout << "C++ MeldCombinations took "
        //           << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()
        //           << " microseconds\n";
        for (int i = 0; i < meld_combos.size(); i++)
        {
            CardIds meld_combo = meld_combos[i];
            Cards unmelded_cards = UnmeldedCards(hand, meld_combo);
            if (stop_on_gin && unmelded_cards.size() == 0)
            {
                // std::cout << "C++ looped over " << total_combos << " combos" << std::endl;
                return {std::make_tuple(0, meld_combo, Cards())};
            }
            int deadwood = GinRummyCardsDeadwood(unmelded_cards);
            if (!max_deadwood.has_value() || deadwood <= max_deadwood.value())
            {
                // SortByRank(unmelded_cards);
                candidate_melds.push_back(std::make_tuple(deadwood, meld_combo, unmelded_cards));
            }
        }
        // end = std::chrono::high_resolution_clock::now();
        // std::cout << "C++ MeldCombinations loop " << n_combos << " took " << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count() << " microseconds\n";
    }
    // std::cout << "C++ looped over " << total_combos << " combos" << std::endl;

    return candidate_melds;
}

std::vector<Cards> MeldIdsToMelds(const CardIds &meld_ids)
{
    std::vector<Cards> melds;
    melds.reserve(3);
    for (int i = 0; i < meld_ids.size(); i++)
    {
        int meld_n = meld_ids[i];
        if (meld_ids[i] != 0)
        {
            melds[meld_n - 1].push_back({CardFromId(i)});
        }
    }
    return {};
}

SortedSplitHand SplitMelds(const Cards &hand, const std::optional<Melds> &melds)
{

    if (melds.has_value())
    {
        Melds chosen_melds = melds.value();
        CardIds chosen_meld_ids;
        chosen_meld_ids.fill(0);
        for (const auto &meld : chosen_melds)
            for (const auto &card : meld)
                chosen_meld_ids[card.ToId()] = 1;
        Cards unmelded = UnmeldedCards(hand, chosen_meld_ids);
        int deadwood = GinRummyCardsDeadwood(unmelded);
        return std::make_tuple(deadwood, SortMelds(chosen_melds), unmelded);
    }

    // int start_result = ProfilerStart("split_melds.prof");
    auto candidate_melds = GetCandidateMelds(hand);
    // for (int i = 0; i < 10'000; i++)
    //     candidate_melds = GetCandidateMelds(hand);

    SplitHand split_hand = *std::min_element(
        candidate_melds.begin(),
        candidate_melds.end(),
        // pick the meld combo with the least deadwood
        [](const SplitHand &a, const SplitHand &b)
        { return std::get<0>(a) < std::get<0>(b); });
    // ProfilerStop();

    // auto end = std::chrono::high_resolution_clock::now();
    // std::cout << "C++ SplitMelds took "
    //           << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()
    //           << " micros" << std::endl;
    int deadwood = std::get<0>(split_hand);
    CardIds chosen_meld_ids = std::get<1>(split_hand);
    Cards unmelded = std::get<2>(split_hand);
    SortByRank(unmelded);
    return std::make_tuple(deadwood, MeldIdsToMelds(chosen_meld_ids), unmelded);
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

bool IsRun(const Cards &meld)
{
    std::vector<Suit> suits;
    std::vector<Rank> ranks;
    for (auto &card : meld)
    {
        std::cout << card.ToString();
        suits.push_back(card.suit);
        ranks.push_back(card.rank);
    }
    std::cout << std::endl;
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
    std::tuple<int, CardIds, Cards, Cards> candidate)
{
    int deadwood = std::get<0>(candidate);
    CardIds meld_ids = std::get<1>(candidate);
    Cards layoffs = std::get<2>(candidate);
    Cards unmelded = std::get<3>(candidate);
    return std::make_tuple(deadwood, MeldIdsToMelds(meld_ids), layoffs, unmelded);
}

std::tuple<int, std::vector<Cards>, Cards, Cards>
LayoffDeadwood(
    const Cards &hand,
    const Melds &opp_melds,
    bool stop_on_zero)
{
    auto [sets, runs] = SplitSetsRuns(opp_melds);
    std::vector<std::tuple<int, CardIds, Cards, Cards>> candidates;

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