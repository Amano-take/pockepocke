import pytest

from game.energy import AttachedEnergies, Energy


def test_energy_enum():
    assert str(Energy.GRASS) == "GRASS"


if __name__ == "__main__":
    pytest.main()
