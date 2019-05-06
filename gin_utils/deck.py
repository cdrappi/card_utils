""" constants to build the deck of cards and score the game """

card_ranks = list('23456789TJQKA')
card_suits = set('cdhs')

cards = [f'{r}{s}' for r in card_ranks for s in card_suits]

card_choices = [(f'{rank}{suit}', f'{rank} of {suit}')
                for (rank, suit) in cards]

suit_ids = {'c': 0, 'd': 1, 'h': 2, 's': 3}
card_values = {
    'A': 1,
    'T': 10,
    'J': 11,
    'Q': 12,
    'K': 13,
    **{d: int(d) for d in '23456789'}
}

card_id_map = {card: index for card, index in enumerate(cards)}
reverse_card_id_map = {index: card for card, index in card_id_map.items()}
