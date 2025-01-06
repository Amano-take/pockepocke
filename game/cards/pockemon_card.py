from __future__ import annotations

import copy
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

# pockemonの状態を表すクラス
class PockemonStatus(Enum):
    NORMAL = "normal"
    PARALYZED = "paralyzed"
    POISONED = "poisoned"
    ASLEEP = "asleep"

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

    def can_attack(self):
        pass

    def set_type(self, type_: PockemonType):
        self.attack_type = type_

    def attack(self, game: Game, plus_damage=0):
        game.waiting_player.active_pockemon.get_damage(self.damage + plus_damage, self.attack_type)


class PockemonCard(Card):
    def __init__(self, player: Player = None, game: Game = None):
        self.name = self.__class__.__name__
        self.energies = AttachedEnergies(player)
        self.game = game

        # 以下設定が必要
        self.hp = self.__class__.hp
        self.type = self.__class__.type
        self.weakness = self.__class__.weakness
        self.attacks: list[PockemonAttack] = copy.deepcopy(self.__class__.attacks)
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

        # can_attack, set_typeを自動設定
        for attack in self.attacks:

            def can_attack():
                return attack.can_attack_hidden(self.energies)

            attack.can_attack = can_attack
            attack.set_type(self.type)
            
        # 状態設定
        self.status = PockemonStatus.NORMAL

    def paralyze(self):
        self.status = PockemonStatus.PARALYZED

    def candidate_attacks(self):
        if self.status == PockemonStatus.PARALYZED:
            return []

        return [attack for attack in self.attacks if attack.can_attack()]

    def attack(self, attack: PockemonAttack):
        attack.attack(self.game)

    def attach_energy(self, energy: Energy):
        self.energies.attach_energy(energy)

    def detach_energy(self, energy: Energy):
        self.energies.detach_energy(energy)

    def get_damage(self, damage: int, enemy_type: PockemonType = None):
        if damage < 0:
            return
        if enemy_type is not None and enemy_type == self.weakness:
            damage += 20
        self.hp -= damage
        if self.hp > 0:
            return

        self.leave_battle()

    def enter_battle(self):
        pass

    def leave_battle(self):
        if self.is_ex:
            self.game.waiting_player.sides += 2
        else:
            self.game.waiting_player.sides += 1

        return

    def use_to_active(self):
        self.game.active_player.active_pockemon = self
        self.game.active_player.hand_pockemon.remove(self)
        return

    def use_to_bench(self):
        self.game.active_player.bench.append(self)
        self.game.active_player.hand_pockemon.remove(self)
        return

    def __str__(self):
        ret = (
            "name: "
            + self.name
            + "   "
            + "hp: "
            + str(self.hp)
            + "   "
            + "type: "
            + str(self.type)
            + "   "
            + "weakness: "
            + str(self.weakness)
            + "   "
            + "retreat_cost: "
            + str(self.retreat_cost)
            + "   "
            + "attached_energies: "
            + str(self.energies)
            + "\n"
        )
        return ret

    def __repr__(self):
        return str(self)


if __name__ == "__main__":
    from game.game import Game
    from game.player import Player
