from __future__ import annotations

from enum import Enum


class Energy(Enum):
    GRASS = 0
    FIRE = 1
    WATER = 2
    LIGHTNING = 3
    PSYCHIC = 4
    FIGHTING = 5
    DARKNESS = 6
    METAL = 7

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class AttachedEnergies:
    def __init__(self, player: Player | None = None):
        self.energies = [0] * len(Energy)
        if player:
            self.energy_values = player.energy_values
        else:
            self.energy_values = [1] * len(Energy)

    def set_player(self, player: Player):
        self.energy_values = player.energy_values

    def attach_energy(self, energy: Energy):
        self.energies[energy.value] += 1

    def detach_energy(self, energy: Energy):
        if self.energies[energy.value] == 0:
            return
        assert self.energies[energy.value] > 0
        self.energies[energy.value] -= 1

    def get_energy(self, energy: Energy):
        return self.energies[energy.value]

    def flatten(self) -> list[Energy]:
        ans = []
        for i, count in enumerate(self.energies):
            ans.extend([Energy(i) for _ in range(count)])
        return ans

    # AttachedEnergiesインスタンスに対して[i]でアクセスできるように
    def __getitem__(self, key):
        return self.energies[key] * self.energy_values[key]

    def get_sum(self):
        return sum(
            self.energies[key] * self.energy_values[key]
            for key in range(len(self.energies))
        )

    def __str__(self):
        ret = ""
        for energy in Energy:
            if self.energies[energy.value] > 0:
                ret += f"{energy}: {self.energies[energy.value]}\n"

        return ret

    def __repr__(self):
        return self.__str__()


class RequiredEnergy:
    def __init__(self, energies: list[Energy], number_any_energy: int):
        self.energies = [0] * len(Energy)
        for energy in energies:
            self.energies[energy.value] += 1
        self.number_any_energy = number_any_energy


if __name__ == "__main__":
    from game.player import Player
