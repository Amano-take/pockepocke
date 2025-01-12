from __future__ import annotations
from game.cards.base_card import Card
from game.cards.pockemon_card import PockemonType
from game.energy import Energy
from game.utils import coin_toss


class TrainerCard(Card):
    def __init__(self):
        self.name = self.__class__.__name__

    def can_use(self, game: Game):
        return True

    def use(self, game: Game):
        game.active_player.hand_trainer.remove(self)
        game.active_player.trash.append(self)

    def can_use(self, game: Game):
        return True

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
        for i, card in enumerate(game.waiting_player.bench):
            selection[i] = f"{card}とactiveを入れ替える"
            candidates[i] = card

        selected = game.waiting_player.select_action(selection)
        game.waiting_player.bench.remove(candidates[selected])
        game.waiting_player.bench.append(game.waiting_player.active_pockemon)
        game.waiting_player.active_pockemon = candidates[selected]
        super().use(game)

    def can_use(self, game: Game):
        return len(game.waiting_player.bench) > 0


class Sakaki(TrainerCard):
    def use(self, game: Game):
        game.active_player.buff(10)


if __name__ == "__main__":
    from game.game import Game
