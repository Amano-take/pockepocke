from game.cards.pockemon_card import PockemonCard, PockemonType, PockemonAttack
from game.energy import RequiredEnergy

class TamaTama(PockemonCard):
    hp = 50
    type = PockemonType.GRASS
    weakness = PockemonType.FIRE
    required_energy = RequiredEnergy([], 1)
    retreat_cost = 1
    class ChottoSeityou(PockemonAttack):
        damage = 0
        RequiredEnergy = RequiredEnergy([], 1)
        
    attacks = [ChottoSeityou]
    
