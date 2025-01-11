import pytest
from unittest.mock import patch
from game.cards import *

from game.deck import Deck
from game.player import Player
from game.energy import Energy
from game.game import Game
from game.exceptions import GameOverException
from .utils.set_lightning import set_lightning

game = Game()

deck_lightning = [
    PikachuEX(),
    PikachuEX(),
    ThunderEX(),
    ThunderEX(),
    Shimama(),
    Shimama(),
    Zeburaika(),
    Zeburaika(),
    Dedenne(),
    HakaseResearcher(),
    HakaseResearcher(),
    Natsume(),
    Natsume(),
    Sakaki(),
    MonsterBall(),
    MonsterBall(),
    Speeder(),
    Speeder(),
    KizuGusuri(),
    KizuGusuri(),
]

player1 = Player(Deck(deck_lightning), [Energy.LIGHTNING])
player2 = Player(Deck(deck_lightning), [Energy.LIGHTNING])

game.set_players(player1, player2)


def test_prepare():
    player = Player(Deck(deck_lightning), [Energy.GRASS])
    player.deck.init_deck()
    player.draw(5)

    with patch.object(player, "select_action", return_value=0) as mock:
        player.prepare()
        mock.assert_called()


def test_energy():
    selevi_player1 = Selevi()
    selevi_player1.set_player(player1, player2)
    selevi_player2 = Selevi()
    selevi_player2.set_player(player2, player1)

    selevi_player1.attach_energy(Energy.GRASS)
    selevi_player2.attach_energy(Energy.GRASS)

    assert selevi_player1.can_attack(0) == False
    assert selevi_player2.can_attack(0) == False

    player1.energy_values[Energy.GRASS.value] = 2

    assert selevi_player1.can_attack(0) == True
    assert selevi_player2.can_attack(0) == False


def test_use_goods():
    game.active_player = player1
    game.waiting_player = player2
    player1.draw(20)

    assert len(player1.hand_goods) == 6
    with patch.object(player1, "select_action", return_value=0) as mock:
        player1.use_goods()
        # 引数のselectionのlenが18であることを確認
        assert len(mock.call_args[0][0]) == 9


def test_attack_pikachu():
    player1.draw(7)
    player2.draw(7)
    player1_pickachu1, player1_pickachu2 = (
        player1.hand_pockemon[0],
        player1.hand_pockemon[1],
    )
    player1_thunder1, player1_thunder2 = (
        player1.hand_pockemon[2],
        player1.hand_pockemon[3],
    )
    player2_pickachu1, player2_pickachu2 = (
        player2.hand_pockemon[0],
        player2.hand_pockemon[1],
    )
    player1.prepare_active_pockemon(player1_pickachu1)
    player2.prepare_active_pockemon(player2_pickachu1)
    player1.prepare_bench_pockemon(player1_pickachu2)
    player1.prepare_bench_pockemon(player1_thunder1)
    player2.prepare_bench_pockemon(player2_pickachu2)
    game.active_player = player1
    game.waiting_player = player2

    assert player1.candidate_attack() == [None]

    player1.active_pockemon.attach_energy(Energy.LIGHTNING)
    player1.active_pockemon.attach_energy(Energy.LIGHTNING)

    attack_list = player1.candidate_attack()

    assert len(attack_list) == 2

    assert player2.active_pockemon.hp == player2.active_pockemon.max_hp

    player1.attack(attack_list[1])

    assert player2.active_pockemon.hp == player2.active_pockemon.max_hp - 60

    game.active_player = player2
    game.waiting_player = player1

    player2.active_pockemon.attach_energy(Energy.LIGHTNING)
    player2.active_pockemon.attach_energy(Energy.LIGHTNING)

    attack_list = player2.candidate_attack()
    assert len(attack_list) == 2

    assert player1.active_pockemon.hp == player1.active_pockemon.max_hp

    player2.attack(attack_list[1])

    assert player1.active_pockemon.hp == player1.active_pockemon.max_hp - 30

    game.active_player = player1
    game.waiting_player = player2

    player1.attack(player1_pickachu1.attacks[0])

    assert player1.sides == 2

    assert player2.active_pockemon is player2_pickachu2
    player1.attack(player1_pickachu2.attacks[0])
    with pytest.raises(GameOverException):
        player1.attack(player1_pickachu2.attacks[0])


def test_select_bench():
    game, player1, player2 = set_lightning()
    player1.draw(7)
    player2.draw(7)
    player1_pickachu1, player1_pickachu2 = (
        player1.hand_pockemon[0],
        player1.hand_pockemon[1],
    )
    player1_thunder1, player1_thunder2 = (
        player1.hand_pockemon[2],
        player1.hand_pockemon[3],
    )
    player2_pickachu1, player2_pickachu2 = (
        player2.hand_pockemon[0],
        player2.hand_pockemon[1],
    )
    player2_thunder1, player2_thunder2 = (
        player2.hand_pockemon[2],
        player2.hand_pockemon[3],
    )
    player1.prepare_active_pockemon(player1_pickachu1)
    player2.prepare_active_pockemon(player2_pickachu1)
    player1.prepare_bench_pockemon(player1_pickachu2)
    player1.prepare_bench_pockemon(player1_thunder1)
    player1.prepare_bench_pockemon(player1_thunder2)
    player2.prepare_bench_pockemon(player2_pickachu2)
    player2.prepare_bench_pockemon(player2_thunder1)
    game.active_player = player1
    game.waiting_player = player2
    # player2のselect_actionをmock
    with patch.object(player2, "select_action", return_value=0) as mock:
        player1.attack(player1_pickachu1.attacks[0])
        player1.attack(player1_pickachu2.attacks[0])
        # mockの引数のselectionのlenが1であることを確認
        assert len(mock.call_args[0][0]) == 2


def test_use_trainers():
    game, player1, player2 = set_lightning()
    player1.draw(20)
    player2.draw(20)
    game.active_player = player1
    game.waiting_player = player2
    with patch.object(player1, "select_action", return_value=0) as mock:
        player1.use_trainer()
        assert len(mock.call_args[0][0]) == 3


def test_pockemon_select():
    game, player1, player2 = set_lightning()
    player1.draw(7)
    player2.draw(7)
    player1_pickachu1, player1_pickachu2 = (
        player1.hand_pockemon[0],
        player1.hand_pockemon[1],
    )
    player1_thunder1, player1_thunder2 = (
        player1.hand_pockemon[2],
        player1.hand_pockemon[3],
    )
    player2_pickachu1, player2_pickachu2 = (
        player2.hand_pockemon[0],
        player2.hand_pockemon[1],
    )
    player2_thunder1, player2_thunder2 = (
        player2.hand_pockemon[2],
        player2.hand_pockemon[3],
    )
    player1.prepare_active_pockemon(player1_pickachu1)
    player2.prepare_active_pockemon(player2_pickachu1)
    player1.prepare_bench_pockemon(player1_pickachu2)
    player1.prepare_bench_pockemon(player1_thunder1)
    player1.prepare_bench_pockemon(player1_thunder2)
    player2.prepare_bench_pockemon(player2_pickachu2)

    game.active_player = player1
    game.waiting_player = player2

    with patch.object(player2, "select_action", return_value=0) as mock:
        player2.use_pockemon_select()
        assert len(mock.call_args[0][0]) == 6

    with patch.object(player1, "select_action", return_value=0) as mock:
        player1.use_pockemon_select()
        assert len(mock.call_args[0][0]) == 1


def test_evolve():
    game, player1, player2 = set_lightning()
    player1.draw(7)
    player2.draw(7)
    player1_shimama1, player1_shimama2 = (
        player1.hand_pockemon[4],
        player1.hand_pockemon[5],
    )
    player1_zeburaika1 = player1.hand_pockemon[6]
    player1.prepare_active_pockemon(player1_shimama1)
    player1.prepare_bench_pockemon(player1_shimama2)

    game.active_player = player1
    game.waiting_player = player2

    assert player1.evolve(player1_shimama1) == True
    assert player1.evolve(player1_shimama2) == False
    assert player1.active_pockemon is player1_zeburaika1


def test_attach_energy_select():
    game, player1, player2 = set_lightning()
    player1.draw(7)
    player2.draw(7)
    player1_pickachu1, player1_pickachu2 = (
        player1.hand_pockemon[0],
        player1.hand_pockemon[1],
    )
    player1_thunder1, player1_thunder2 = (
        player1.hand_pockemon[2],
        player1.hand_pockemon[3],
    )
    player2_pickachu1, player2_pickachu2 = (
        player2.hand_pockemon[0],
        player2.hand_pockemon[1],
    )
    player1.prepare_active_pockemon(player1_pickachu1)
    player2.prepare_active_pockemon(player2_pickachu1)
    player1.prepare_bench_pockemon(player1_pickachu2)
    player1.prepare_bench_pockemon(player1_thunder1)
    player2.prepare_bench_pockemon(player2_pickachu2)
    game.active_player = player1
    game.waiting_player = player2

    player1.get_energy()

    with patch.object(player1, "select_action", return_value=1) as mock:
        player1.attach_energy_select()
        assert len(mock.call_args[0][0]) == 4
        assert player1_pickachu1.energies.get_sum() == 1
        assert player1_pickachu2.energies.get_sum() == 0


def test_evolve_select():
    game, player1, player2 = set_lightning()
    player1.draw(8)
    player2.draw(8)
    player1_shimama1, player1_shimama2 = (
        player1.hand_pockemon[4],
        player1.hand_pockemon[5],
    )
    player1_zeburaika1, player1_zeburaika2 = (
        player1.hand_pockemon[6],
        player1.hand_pockemon[7],
    )
    player1.prepare_active_pockemon(player1_shimama1)
    player1.prepare_bench_pockemon(player1_shimama2)

    game.active_player = player1
    game.waiting_player = player2

    with patch.object(player1, "select_action", return_value=3) as mock:
        player1.evolve_select()
        assert len(mock.call_args[0][0]) == 4

    assert player1.active_pockemon.name == "Zeburaika"
    assert player1.bench[0].name == "Zeburaika"


def _test_prepare():
    deck = [TamaTama(), Nassy(), Selevi()]
    for _ in range(17):
        deck.append(Tsutaja())

    player = Player(Deck(deck), [Energy.GRASS])
    player.deck.init_deck()
    player.draw(5)
    player.prepare()


if __name__ == "__main__":
    test_attack_pikachu()
