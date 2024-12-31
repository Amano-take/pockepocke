from game.cards.pockemon_cards.grass_cards import TamaTama
from game.energy import Energy, AttachedEnergies, RequiredEnergy
from game.cards.pockemon_card import PockemonCard, PockemonType, PockemonAttack
from ipdb import set_trace


def test_tama_tama():
    tama_tama = TamaTama()
    assert tama_tama.hp == 50
    assert tama_tama.type == PockemonType.GRASS
    assert tama_tama.weakness == PockemonType.FIRE
    assert tama_tama.retreat_cost == 1
    assert len(tama_tama.attacks) == 1
    assert tama_tama.attacks[0].name == "ChottoSeityou"
    assert tama_tama.energies.get_sum() == 0
    assert tama_tama.attacks[0].can_attack() == False
    
    tama_tama.energies.attach_energy(Energy.GRASS)
    
    assert tama_tama.energies.get_sum() == 1
    assert tama_tama.attacks[0].can_attack() == True
    
    
if __name__ == "__main__":
    test_tama_tama()
    print("test_tama_tama passed")