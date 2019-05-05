""" constants to build the deck of cards and score the game """

card_ranks = list('23456789TJQKA')
card_suits = set('cdhs')

card_choices = [(f'{rank}{suit}', f'{rank} of {suit}')
                for rank in card_ranks for suit in card_suits]

card_values = {
    'A': 1,
    'T': 10,
    'J': 11,
    'Q': 12,
    'K': 13,
    **{d: int(d) for d in '23456789'}
}
