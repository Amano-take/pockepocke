import random

from game.cards.base_card import Card
from game.cards.pockemon_card import PockemonCard

class Deck:
    def __init__(self, cards: list[Card]):
        self.cards = cards
        
    def draw(self):
        return self.cards.pop(0)
    
    def shuffle(self):
        random.shuffle(self.cards)
        
    def init_deck(self):
        # デッキに少なくともシードポケモンが一枚あるようにする
        while True:
            self.shuffle()
            for i in range(5):
                if isinstance(self.cards[i], PockemonCard):
                    card: PockemonCard = self.cards[i]
                    if card.is_seed:
                        break
            else:
                continue
            break
        
        
    def validate(self):
        assert len(self.cards) == 20
        for card in self.cards:
            assert isinstance(card, Card)
            
        # TODO: 各クラスのカードが2枚までかどうか
        
        
    
        