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

    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._count = 1
        return obj

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return self.name


class AttachedEnergies:
    def __init__(self):
        self.energies = [0] * len(Energy)

    def attach_energy(self, energy: Energy):
        self.energies[energy.value] += 1

    def detach_energy(self, energy: Energy):
        self.energies[energy.value] -= 1

    def get_energy(self, energy: Energy):
        return self.energies[energy.value]

    # AttachedEnergiesインスタンスに対して[i]でアクセスできるように
    def __getitem__(self, key):
        return self.energies[key] * Energy(key).count

    def get_sum(self):
        return sum(self.energies[key] * Energy(key).count for key in range(len(self.energies)))

    def __str__(self):
        for energy in Energy:
            if self.energies[energy.value] > 0:
                print(f"{energy}: {self.energies[energy.value]}")

    def __repr__(self):
        return str(self.energies)


class RequiredEnergy:
    def __init__(self, energies: list[Energy], number_any_energy: int):
        self.energies = [0] * len(Energy)
        for energy in energies:
            self.energies[energy.value] += 1
        self.number_any_energy = number_any_energy
