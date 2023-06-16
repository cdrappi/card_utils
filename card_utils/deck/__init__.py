""" constants to build the deck of cards and score the game """

from typing import List, Tuple

ranks: List[str] = list("23456789TJQKA")
suits: List[str] = list("cdhs")

cards: List[str] = [f"{r}{s}" for r in ranks for s in suits]
_cards_rds: List[Tuple[str, str]] = [(r, s) for r in ranks for s in suits]

card_choices = [
    (f"{rank}{suit}", f"{rank} of {suit}") for (rank, suit) in _cards_rds
]

suit_ids = {"c": 0, "d": 1, "h": 2, "s": 3}
rank_ids = {rank: index for index, rank in enumerate(ranks)}

card_id_map = {card: index for index, card in enumerate(cards)}
reverse_card_id_map = {index: card for card, index in card_id_map.items()}

digit_map = {d: int(d) for d in "23456789"}
common_rank_to_value = {"T": 10, "J": 11, "Q": 12, "K": 13}
common_rank_to_value.update(digit_map)

ace_high_rank_to_value = {"A": 14}
ace_high_rank_to_value.update(common_rank_to_value)

ace_low_rank_to_value = {"A": 1}
ace_low_rank_to_value.update(common_rank_to_value)

rank_to_value = ace_low_rank_to_value

value_to_rank = {14: "A", 1: "A"}
value_to_rank.update({v: r for r, v in common_rank_to_value.items()})
