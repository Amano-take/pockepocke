from __future__ import annotations

import copy
from enum import Enum

from game.cards.base_card import Card
from game.energy import AttachedEnergies, Energy, RequiredEnergy
from game.exceptions import GameOverException


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
    damage = 10
    required_energy: RequiredEnergy = RequiredEnergy([Energy.DARKNESS], 1)

    def __init__(self):
        self.name = self.__class__.__name__
        self.damage = self.__class__.damage
        self.required_energy: RequiredEnergy = self.__class__.required_energy

    def can_attack_hidden(self, energies: AttachedEnergies):
        for i in range(len(Energy)):
            if self.required_energy.energies[i] > energies.energies[i]:
                return False

        if (
            energies.get_sum()
            < sum(self.required_energy.energies)
            + self.required_energy.number_any_energy
        ):
            return False

        return True

    def target_list(self, game: Game) -> list[PockemonCard]:
        return [game.waiting_player.active_pockemon]

    def set_type(self, type_: PockemonType):
        self.attack_type = type_

    def attack(self, game: Game, target_pockemon: PockemonCard | None = None):
        if target_pockemon is None:
            target_pockemon = game.waiting_player.active_pockemon
        target_pockemon.get_damage(game, self.damage, self.attack_type)


class PockemonCard(Card):
    hp: int = 100
    type: PockemonType = PockemonType.NORMAL
    weakness: PockemonType = PockemonType.NORMAL
    attacks: list[PockemonAttack] = []
    retreat_cost: int = 1
    previous_pockemon: PockemonCard | None = None
    next_pockemon: PockemonCard | None = None
    is_ex: bool = False

    def __init__(self):
        self.name = self.__class__.__name__
        self.energies = AttachedEnergies()

        # 以下設定が必要
        self.hp = self.__class__.hp
        self.max_hp = self.__class__.hp
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

        # set_typeを自動設定
        for attack in self.attacks:
            attack.set_type(self.type)

        # 状態設定
        self.status = PockemonStatus.NORMAL

        # super
        super().__init__()

    def set_player(self, player: Player, opponent: Player):
        self.player = player.name
        self.energies.set_player(player)
        self.opponent = opponent.name

    def can_retreat(self, buffer: int = 0) -> bool:
        return self.energies.get_sum() + buffer >= self.retreat_cost

    def retreat(self, buffer: int = 0, loss_energies: list[Energy] = []):
        assert self.retreat_cost - buffer == len(loss_energies)
        for energy in loss_energies:
            self.energies.detach_energy(energy)

    def can_attack(self, attack: PockemonAttack | int):
        if isinstance(attack, int):
            attack = self.attacks[attack]

        return attack.can_attack_hidden(self.energies)

    def paralyze(self):
        self.status = PockemonStatus.PARALYZED

    def candidate_attacks(self):
        if self.status == PockemonStatus.PARALYZED:
            return []

        return [attack for attack in self.attacks if self.can_attack(attack)]

    def attack(self, attack: PockemonAttack):
        attack.attack(self.game)

    def heal(self, heal: int):
        self.hp += heal
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attach_energy(self, energy: Energy):
        self.energies.attach_energy(energy)

    def detach_energy(self, energy: Energy):
        self.energies.detach_energy(energy)

    def get_damage(
        self, game: Game, damage: int, enemy_type: PockemonType | None = None
    ):
        if damage < 0:
            return True
        my_player = game.get_player_by_name(self.player)
        opponent = game.get_player_by_name(self.opponent)
        if (
            enemy_type is not None
            and enemy_type == self.weakness
            and my_player.active_pockemon is self
        ):
            damage += 20
        assert game.active_player
        if game.active_player.attack_buff_value > 0:
            damage += game.active_player.attack_buff_value
        self.hp -= damage
        if self.hp > 0:
            return True

        return self.leave_battle(game)

    def enter_battle(self):
        self.feature_passive()

    def feature_active(self):
        pass

    def feature_passive(self):
        pass

    def reset_feature_passive(self):
        pass

    def leave_battle(self, game: Game):
        """
        return:
            True ゲームを続ける
            False ゲーム終了
        """
        self.reset_feature_passive()
        my_player = game.get_player_by_name(self.player)
        opponent = game.get_player_by_name(self.opponent)

        if self.is_ex:
            opponent.sides += 2
        else:
            opponent.sides += 1

        # ゲームの終了判定
        if len(opponent.bench) == 0:
            raise GameOverException(opponent)

        if opponent.sides >= 3:
            raise GameOverException(opponent)

        my_player.select_bench()
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
        # オブジェクトのメモリアドレスを返す
        return super().__repr__()


if __name__ == "__main__":
    from game.game import Game
    from game.player import Player
