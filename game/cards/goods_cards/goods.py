from __future__ import annotations

from game.cards.base_card import Card
from game.cards.pockemon_card import PockemonCard, PockemonType
import random


class GoodsCard(Card):
    def __init__(self):
        self.name = self.__class__.__name__
        super().__init__()

    def can_use(self, game: Game) -> bool | list[PockemonCard]:
        return True

    def use(self, game: Game):
        game.active_player.hand_goods.remove(self)
        game.active_player.trash.append(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class KizuGusuri(GoodsCard):
    def use(self, game: Game, target: PockemonCard):
        target.heal(20)
        super().use(game)

    def can_use(self, game: Game):
        """
        使えるポケモンの候補を返す
        """
        res = []
        for pockemon in [game.active_player.active_pockemon] + game.active_player.bench:
            if pockemon.hp < pockemon.max_hp:
                res.append(pockemon)

        if len(res) == 0:
            return False

        return res


class MonsterBall(GoodsCard):
    def use(self, game: Game):
        if card := game.active_player.deck.draw_seed_pockemon():
            game.active_player.hand_pockemon.append(card)
        super().use(game)


class Speeder(GoodsCard):
    def use(self, game: Game):
        game.active_player.retreat_buff(1)
        super().use(game)


class RedCard(GoodsCard):
    def use(self, game: Game):
        game.waiting_player.deck.cards.extend(game.waiting_player.hand_pockemon)
        game.waiting_player.hand_pockemon = []
        game.waiting_player.deck.cards.extend(game.waiting_player.hand_goods)
        game.waiting_player.hand_goods = []
        game.waiting_player.deck.cards.extend(game.waiting_player.hand_trainer)
        game.waiting_player.hand_trainer = []
        game.waiting_player.deck.shuffle()
        game.waiting_player.draw(3)
        super().use(game)


class PockemonnoHue(GoodsCard):
    def use(self, game: Game):
        if len(game.waiting_player.bench) == 3:
            return

        selection = {}
        candidates = {}
        for card in game.waiting_player.trash:
            if isinstance(card, PockemonCard) and card.is_seed:
                selection[len(selection)] = f"{card.name}をベンチに出す"
                candidates[len(candidates)] = card
        if len(selection) == 0:
            return

        i = game.active_player.select_action(selection)
        game.waiting_player.bench.append(candidates[i])
        game.waiting_player.trash.remove(candidates[i])

        super().use(game)

    def can_use(self, game: Game):
        if len(game.waiting_player.bench) == 3:
            return False
        else:
            return True


class MaboroshinoSekibann(GoodsCard):
    def use(self, game: Game):
        card = game.active_player.deck.draw()
        if isinstance(card, PockemonCard) and card.type == PockemonType.DARKNESS:
            game.active_player.hand_pockemon.append(card)
        else:
            game.active_player.deck.extend_last(card)

        super().use(game)


class PockemonConnection(GoodsCard):
    def can_use(self, game: Game) -> list[PockemonCard]:
        return game.active_player.hand_pockemon

    def use(self, game: Game, target: PockemonCard):
        # swap hand and deck
        cand = []
        for i, card in enumerate(game.active_player.deck.cards):
            if isinstance(card, PockemonCard):
                cand.append(i)

        if len(cand) == 0:
            return

        hand_index = game.active_player.hand_pockemon.index(target)

        # randomly
        i = random.randint(0, len(cand) - 1)

        (
            game.active_player.deck.cards[cand[i]],
            game.active_player.hand_pockemon[hand_index],
        ) = (
            game.active_player.hand_pockemon[hand_index],
            game.active_player.deck.cards[cand[i]],
        )

        super().use(game)


if __name__ == "__main__":
    from game.game import Game
