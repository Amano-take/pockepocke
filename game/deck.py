from __future__ import annotations
import random
from copy import deepcopy

from game.cards.base_card import Card
from game.cards.pockemon_card import PockemonCard


class Deck:
    def __init__(self, cards: list[Card]):
        # クラスを取得してインスタンスを作成
        self.cards: list[Card] = []
        for card in cards:
            self.cards.append(type(card)())

    def draw(self):
        return self.cards.pop(0)

    def extend_last(self, card: Card):
        self.cards.append(card)

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

    def set_player(self, player: Player):
        self.player = player
        for card in self.cards:
            card.set_player(player, player.opponent)
            card.set_game(player.game)

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


if __name__ == "__main__":
    from game.player import Player
