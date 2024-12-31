from enum import Enum

class Energy(Enum):
    GRASS = 1
    FIRE = 2
    WATER = 3
    LIGHTNING = 4
    PSYCHIC = 5
    FIGHTING = 6
    DARKNESS = 7
    METAL = 8

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return self.name

class AttachedEnergies:
    def __init__(self):
        self.energies = [0] * len(Energy)

    def attach_energy(self, energy):
        self.energies[energy.value - 1] += 1

    def detach_energy(self, energy):
        self.energies[energy.value - 1] -= 1

    def get_energy(self, energy):
        return self.energies[energy.value - 1]
    
    def get_sum(self):
        return sum(self.energies)

    def __str__(self):
        for energy in Energy:
            if self.energies[energy.value - 1] > 0:
                print(f"{energy}: {self.energies[energy.value - 1]}")

    def __repr__(self):
        return str(self.energies)
    
class RequiredEnergy:
    def __init__(self, energies: list[Energy], number_any_energy: int):
        self.energies = [0] * len(Energy)
        for energy in energies:
            self.energies[energy.value - 1] += 1
        self.number_any_energy = number_any_energy
        
            
    
    

