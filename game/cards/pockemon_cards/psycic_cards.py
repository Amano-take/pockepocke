from __future__ import annotations

from game.cards.pockemon_card import PockemonCard, PockemonType, PockemonAttack
from game.energy import RequiredEnergy
from game.energy import Energy


class MewtwoEX(PockemonCard):
    hp = 150
    type = PockemonType.PSYCHIC
    weakness = PockemonType.METAL
    retreat_cost = 2
    is_ex = True

    class Nendoudan(PockemonAttack):
        damage = 50
        required_energy = RequiredEnergy([Energy.PSYCHIC], 1)

    class PsychoDrive(PockemonAttack):
        damage = 150
        required_energy = RequiredEnergy([Energy.PSYCHIC, Energy.PSYCHIC], 2)

        def attack(self, game: Game):
            assert game.active_player.active_pockemon.name == "MewtwoEX"
            game.active_player.active_pockemon.detach_energy(Energy.PSYCHIC)
            game.active_player.active_pockemon.detach_energy(Energy.PSYCHIC)
            super().attack(game)

    attacks = [Nendoudan(), PsychoDrive()]


class MewEX(PockemonCard):
    hp = 130
    type = PockemonType.PSYCHIC
    weakness = PockemonType.METAL
    retreat_cost = 1
    is_ex = True

    class PhycoShot(PockemonAttack):
        damage = 20
        required_energy = RequiredEnergy([Energy.PSYCHIC], 0)

    class GenomHack(PockemonAttack):
        damage = 0
        required_energy = RequiredEnergy([], 3)

        def attack(self, game: Game, target: PockemonAttack):
            target.attack(game)

        def target_list(self, game) -> list[PockemonAttack]:
            return game.waiting_player.active_pockemon.attacks

    attacks = [PhycoShot(), GenomHack()]


class Ralts(PockemonCard):
    hp = 60
    type = PockemonType.PSYCHIC
    weakness = PockemonType.METAL
    retreat_cost = 1
    next_pockemon = "Kirlia"

    class Teleport(PockemonAttack):
        damage = 0
        required_energy = RequiredEnergy([], 1)

        def target_list(self, game: Game) -> list[PockemonCard]:
            return game.active_player.bench

        def attack(self, game: Game, target: PockemonCard):
            assert target in game.active_player.bench

            game.active_player.bench.remove(target)
            game.active_player.bench.append(game.active_player.active_pockemon)
            game.active_player.active_pockemon = target

    attacks = [Teleport()]


class Kirlia(PockemonCard):
    hp = 80
    type = PockemonType.PSYCHIC
    weakness = PockemonType.METAL
    retreat_cost = 1
    previous_pockemon = "Ralts"
    next_pockemon = "Cernight"

    class Binta(PockemonAttack):
        damage = 20
        required_energy = RequiredEnergy([], 1)

    attacks = [Binta()]


class Cernight(PockemonCard):
    hp = 100
    type = PockemonType.PSYCHIC
    weakness = PockemonType.METAL
    retreat_cost = 2
    previous_pockemon = "Kirlia"

    class PsychoShot(PockemonAttack):
        damage = 60
        required_energy = RequiredEnergy([Energy.PSYCHIC], 1)

    attacks = [PsychoShot()]

    def feature_active(self, game: Game):
        player = game.get_player_by_name(self.player)
        player.active_pockemon.attach_energy(Energy.PSYCHIC)


if __name__ == "__main__":
    from game.game import Game
