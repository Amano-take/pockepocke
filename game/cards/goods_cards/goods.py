from __future__ import annotations
from game.cards.base_card import Card
from game.cards.pockemon_card import PockemonCard
from game.cards.pockemon_card import PockemonType


class GoodsCard(Card):
    def __init__(self):
        self.name = self.__class__.__name__

    def can_use(self):
        return True

    def use(self, game: Game):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class KizuGusuri(GoodsCard):
    def use(self, game: Game):
        game.active_player.active_pockemon.hp += 20
        game.active_player.hand_goods.remove(self)
        game.active_player.trash.append(self)


class MonsterBall(GoodsCard):
    def use(self, game: Game):
        game.active_player.hand_pockemon.append(game.active_player.deck.draw_seed_pockemon())
        game.active_player.hand_goods.remove(self)
        game.active_player.trash.append(self)


class Speeder(GoodsCard):
    def use(self, game: Game):
        game.active_player.active_pockemon.retreat_cost -= 1
        for bench_pockemon in game.active_player.bench:
            bench_pockemon.retreat_cost -= 1
        game.active_player.hand_goods.remove(self)
        game.active_player.trash.append(self)

        def end_process(game: Game):
            game.active_player.active_pockemon.retreat_cost += 1
            for bench_pockemon in game.active_player.bench:
                bench_pockemon.retreat_cost += 1

        game.active_player.processes_at_end_of_turn.append(end_process)


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
        game.active_player.hand_goods.remove(self)
        game.active_player.trash.append(self)


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

        game.active_player.hand_goods.remove(self)
        game.active_player.trash.append(self)

    def can_use(self, game: Game):
        if len(game.waiting_player.bench) == 3:
            return False


class MaboroshinoSekibann(GoodsCard):
    def use(self, game: Game):
        card = game.active_player.deck.draw()
        if isinstance(card, PockemonCard) and card.type == PockemonType.DARKNESS:
            game.active_player.hand_pockemon.append(card)
        else:
            game.active_player.deck.extend_last(card)

        game.active_player.hand_goods.remove(self)
        game.active_player.trash.append(self)


if __name__ == "__main__":
    from game.game import Game
