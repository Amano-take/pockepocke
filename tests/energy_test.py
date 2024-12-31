import pytest
from game.energy import Energy

def test_energy_enum():
    assert str(Energy.GRASS) == "grasa"
    
if __name__ == "__main__":
    pytest.main()