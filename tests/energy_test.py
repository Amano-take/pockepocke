import pytest
from game.energy import Energy, AttachedEnergies


def test_energy_enum():
    assert str(Energy.GRASS) == "grass"


def test_energy_value():
    assert Energy.GRASS.count == 1
    assert Energy.FIRE.count == 1

    Energy.GRASS.count = 2
    assert Energy.GRASS.count == 2
    assert Energy.FIRE.count == 1

    attached_energy = AttachedEnergies()
    attached_energy.attach_energy(Energy.GRASS)
    attached_energy.attach_energy(Energy.FIRE)

    assert attached_energy[Energy.GRASS.value] == 2
    assert attached_energy.get_sum() == 3

    Energy.GRASS.count = 1


if __name__ == "__main__":
    pytest.main()
