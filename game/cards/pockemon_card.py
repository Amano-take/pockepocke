from __future__ import annotations

from enum import Enum
from game.energy import Energy, AttachedEnergies, RequiredEnergy
from game.cards.base_card import Card


class PockemonType(Enum):
    NORMAL = "normal"
    GRASS = "grass"
    FIRE = "fire"
    WATER = "water"
    LIGHTNING = "lightning"
    PSYCHIC = "psychic"
    FIGHTING = "fighting"
    DARKNESS = "darkness"
    METAL = "metal"
    DRAGON = "dragon"

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return self.name


class PockemonAttack:

    def __init__(self):
        self.name = self.__class__.__name__
        self.damage = self.__class__.damage
        self.required_energy: RequiredEnergy = self.__class__.required_energy

    def can_attack_hidden(self, energies: AttachedEnergies):
        for i in range(len(Energy)):
            if self.required_energy.energies[i] > energies.energies[i]:
                return False

        if energies.get_sum() < sum(self.required_energy.energies) + self.required_energy.number_any_energy:
            return False

        return True

    def other_effect(self, game: Game):
        pass

    def can_attack(self):
        pass

    def attack(self, game: Game):

        self.other_effect()


class PockemonCard(Card):
    def __init__(self):
        self.name = self.__class__.__name__
        self.energies = AttachedEnergies()

        # 以下設定が必要
        self.hp = self.__class__.hp
        self.type = self.__class__.type
        self.weakness = self.__class__.weakness
        self.attacks: list[PockemonAttack] = self.__class__.attacks
        self.retreat_cost = self.__class__.retreat_cost
        if hasattr(self.__class__, "previous_pockemon"):
            self.previous_pockemon = self.__class__.previous_pockemon
        else:
            self.previous_pockemon = None

        if hasattr(self.__class__, "next_pockemon"):
            self.next_pockemon = self.__class__.next_pockemon
        else:
            self.next_pockemon = None

        # is_exがあるならば設定
        if hasattr(self.__class__, "is_ex"):
            self.is_ex = self.__class__.is_ex
        else:
            self.is_ex = False

        if self.previous_pockemon is None:
            self.is_seed = True
        else:
            self.is_seed = False

        # can_attackを自動設定
        for attack in self.attacks:

            def can_attack():
                return attack.can_attack_hidden(self.energies)

            attack.can_attack = can_attack

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def attach_energy(self, energy: Energy):
        self.energies.attach_energy(energy)


if __name__ == "__main__":
    from game.game import Game
