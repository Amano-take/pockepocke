import random

from game.cards.base_card import Card
from game.cards.pockemon_card import PockemonCard


class Deck:
    def __init__(self, cards: list[Card]):
        self.cards = cards[:]

    def draw(self):
        return self.cards.pop(0)

    def draw_seed_pockemon(self):
        for card in self.cards:
            if isinstance(card, PockemonCard):
                if card.is_seed:
                    # TODO: 化石ポケモンをのぞく処理をする
                    return_card = card
                    self.cards.remove(card)
                    self.shuffle()
                    return return_card
        return None

    def shuffle(self):
        random.shuffle(self.cards)

    def init_deck(self):
        from game.cards.pockemon_card import PockemonCard  # Moved import here

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
