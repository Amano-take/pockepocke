from __future__ import annotations

from game.cards.pockemon_card import PockemonCard, PockemonType, PockemonAttack
from game.energy import RequiredEnergy
from game.energy import Energy
from game.utils import coin_toss


class PikachuEX(PockemonCard):
    hp = 120
    type = PockemonType.LIGHTNING
    weakness = PockemonType.FIGHTING
    retreat_cost = 1
    is_ex = True

    class ElechiCircle(PockemonAttack):
        damage = 0
        required_energy = RequiredEnergy([Energy.LIGHTNING, Energy.LIGHTNING], 0)

        def attack(self, game: Game):
            self.damage = 30 * len(game.active_player.bench)
            super().attack(game)

    attacks = [
        ElechiCircle(),
    ]


class ThunderEX(PockemonCard):
    hp = 130
    type = PockemonType.LIGHTNING
    weakness = PockemonType.LIGHTNING
    retreat_cost = 1
    is_ex = True

    class Tsutsuku(PockemonAttack):
        damage = 20
        required_energy = RequiredEnergy([Energy.LIGHTNING], 0)

    # ハリケーンサンダー
    class HurricaneThunder(PockemonAttack):
        damage = 0
        required_energy = RequiredEnergy(
            [Energy.LIGHTNING, Energy.LIGHTNING, Energy.LIGHTNING], 0
        )

        def attack(self, game: Game):
            count = 0
            for i in range(4):
                if coin_toss():
                    count += 1
            self.damage = 50 * count

            super().attack(game)

    attacks = [
        Tsutsuku(),
        HurricaneThunder(),
    ]


class Shimama(PockemonCard):
    hp = 60
    type = PockemonType.LIGHTNING
    weakness = PockemonType.FIGHTING
    retreat_cost = 1
    next_pockemon = "Zeburaika"

    # エレキック
    class Elekick(PockemonAttack):
        damage = 20
        required_energy = RequiredEnergy([Energy.LIGHTNING], 0)

    attacks = [
        Elekick(),
    ]


class Zeburaika(PockemonCard):
    hp = 90
    type = PockemonType.LIGHTNING
    weakness = PockemonType.FIGHTING
    retreat_cost = 1
    previous_pockemon = "Shimama"

    # サンダーアロー
    class ThunderArrow(PockemonAttack):
        damage = 30
        required_energy = RequiredEnergy([Energy.LIGHTNING], 0)

        def attack(self, game: Game):
            selection = {}
            candidates: dict[int, PockemonCard] = {}
            pockemons = [
                game.waiting_player.active_pockemon
            ] + game.waiting_player.bench
            for i, pockemon in enumerate(pockemons):
                selection[i] = f"{pockemon}に30ダメージ"
                candidates[i] = pockemon

            i = game.active_player.select_action(selection)
            if i == 0:
                candidates[i].get_damage(30, PockemonType.LIGHTNING)
            else:
                candidates[i].get_damage(30, None)

        def target_list(self, game):
            return [game.waiting_player.active_pockemon] + game.waiting_player.bench

    attacks = [
        ThunderArrow(),
    ]


class Dedenne(PockemonCard):
    hp = 60
    type = PockemonType.LIGHTNING
    weakness = PockemonType.FIGHTING
    retreat_cost = 1

    # 電気ショック
    class ElectricShock(PockemonAttack):
        damage = 10
        required_energy = RequiredEnergy([Energy.LIGHTNING], 0)

        def attack(self, game: Game):
            super().attack(game)
            if coin_toss():
                game.waiting_player.active_pockemon.paralyze()

    attacks = [
        ElectricShock(),
    ]


if __name__ == "__main__":
    from game.game import Game
