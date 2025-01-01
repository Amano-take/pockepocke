from game.cards.pockemon_card import PockemonCard, PockemonType, PockemonAttack
from game.energy import RequiredEnergy
from game.energy import Energy


class TamaTama(PockemonCard):
    hp = 50
    type = PockemonType.GRASS
    weakness = PockemonType.FIRE
    retreat_cost = 1
    next_pockemon = "Nassy"

    class ChottoSeityou(PockemonAttack):
        damage = 0
        required_energy = RequiredEnergy([], 1)

    attacks = [ChottoSeityou()]


class Nassy(PockemonCard):
    hp = 130
    type = PockemonType.GRASS
    weakness = PockemonType.FIRE
    retreat_cost = 3
    previous_pockemon = "TamaTama"

    class Phychokinesis(PockemonAttack):
        damage = 80
        required_energy = RequiredEnergy([Energy.GRASS], 3)

    attacks = [Phychokinesis()]


class Selevi(PockemonCard):
    hp = 130
    type = PockemonType.GRASS
    weakness = PockemonType.FIRE
    retreat_cost = 1
    is_ex = True

    class PowerfulBloom(PockemonAttack):
        damage = 50
        required_energy = RequiredEnergy([Energy.GRASS], 1)

    attacks = [PowerfulBloom()]


class Tsutaja(PockemonCard):
    hp = 70
    type = PockemonType.GRASS
    weakness = PockemonType.FIRE
    retreat_cost = 1

    class TsuruNoMuchi(PockemonAttack):
        damage = 40
        required_energy = RequiredEnergy([Energy.GRASS], 1)

    attacks = [TsuruNoMuchi()]


class Janobii(PockemonCard):
    hp = 80
    type = PockemonType.GRASS
    weakness = PockemonType.FIRE
    retreat_cost = 1
    previous_pockemon = "tsutaja"

    class TsuruNoMuchi(PockemonAttack):
        damage = 50
        required_energy = RequiredEnergy([Energy.GRASS], 1)

    attacks = [TsuruNoMuchi()]


class Jaroda(PockemonCard):
    hp = 110
    type = PockemonType.GRASS
    weakness = PockemonType.FIRE
    retreat_cost = 3
    previous_pockemon = "janobii"

    class TsuruNoMuchi(PockemonAttack):
        damage = 70
        required_energy = RequiredEnergy([Energy.GRASS], 3)

    attacks = [TsuruNoMuchi()]


class Nemashu(PockemonCard):
    hp = 60
    type = PockemonType.GRASS
    weakness = PockemonType.FIRE
    retreat_cost = 1

    class Butsukaru(PockemonAttack):
        damage = 20
        required_energy = RequiredEnergy([Energy.GRASS], 0)

    attacks = [Butsukaru()]


class Masheedo(PockemonCard):
    hp = 90
    type = PockemonType.GRASS
    weakness = PockemonType.FIRE
    retreat_cost = 2
    previous_pockemon = "Nemashu"

    class YureruBoshi(PockemonAttack):
        damage = 50
        required_energy = RequiredEnergy([Energy.GRASS] * 2, 0)

    attacks = [YureruBoshi()]


class Dadarin(PockemonCard):
    hp = 100
    type = PockemonType.GRASS
    weakness = PockemonType.FIRE
    retreat_cost = 2

    class EnergyWhip(PockemonAttack):
        damage = 20
        required_energy = RequiredEnergy([Energy.GRASS], 0)

    attacks = [EnergyWhip()]
