from __future__ import annotations

from game.cards.pockemon_card import PockemonCard, PockemonType
from game.cards.base_card import Card
from game.energy import Energy
from game.utils import coin_toss


class TrainerCard(Card):
    def __init__(self):
        self.name = self.__class__.__name__
        super().__init__()

    def can_use(self, game: Game) -> bool | list[PockemonCard]:
        return True

    def use(self, game: Game, target: PockemonCard | None = None):
        assert game.active_player
        assert self in game.active_player.hand_trainer
        game.active_player.hand_trainer.remove(self)
        game.active_player.trash.append(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Erika(TrainerCard):
    def use(self, game: Game):
        game.active_player.active_pockemon.hp += 50
        super().use(game)

    def can_use(self, game: Game):
        return game.active_player.active_pockemon.type == PockemonType.GRASS


class Kasumi(TrainerCard):
    def use(self, game: Game):
        num_energy = 0
        while True:
            if coin_toss():
                game.active_player.active_pockemon.attach_energy(Energy.WATER)
                num_energy += 1
            else:
                break
        super().use(game)
        return num_energy

    def can_use(self, game: Game):
        return game.active_player.active_pockemon.type == PockemonType.WATER


class Katsura(TrainerCard):
    # TODO: これどうするか考える。
    pass


class HakaseResearcher(TrainerCard):
    def use(self, game: Game):
        game.active_player.draw(2)
        super().use(game)


class Natsume(TrainerCard):
    def use(self, game: Game):
        selection = {}
        candidates = {}
        action = {}
        for i, card in enumerate(game.waiting_player.bench):
            selection[i] = f"[opponent_trainer] {card}とactiveを入れ替える"

            def f(card=card):
                game.waiting_player.bench.remove(card)
                game.waiting_player.bench.append(game.waiting_player.active_pockemon)
                game.waiting_player.active_pockemon = card

            action[i] = f

        selected = game.waiting_player.select_action(selection, action)
        action[selected]()
        super().use(game)

    def can_use(self, game: Game):
        return len(game.waiting_player.bench) > 0


class Sakaki(TrainerCard):
    def use(self, game: Game):
        game.active_player.attack_buff(10)
        super().use(game)


class Leaf(TrainerCard):
    def use(self, game: Game):
        game.active_player.retreat_buff(2)
        super().use(game)


# トレーナーカードリスト
TRAINER_CARDS: list[type[TrainerCard]] = [
    Erika,
    Kasumi,
    HakaseResearcher,
    Natsume,
    Sakaki,
    Leaf,
]

if __name__ == "__main__":
    from game.game import Game
