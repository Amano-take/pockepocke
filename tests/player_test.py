from unittest.mock import patch

import pytest

from game.cards import *
from game.deck import Deck
from game.energy import Energy
from game.exceptions import GameOverException
from game.game import Game
from game.player import Player

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


def get_game_player():
    game = Game()
    player1 = Player(Deck(deck_lightning), [Energy.LIGHTNING])
    player2 = Player(Deck(deck_lightning), [Energy.LIGHTNING])
    game.set_players(player1, player2)
    return game, player1, player2


def test_prepare():
    game, player1, player2 = get_game_player()
    player1.draw(5)

    with patch.object(player1, "select_action", return_value=0) as mock:
        player1.prepare()
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


def test_use_goods_select():
    game.active_player = player1
    game.waiting_player = player2
    player1.draw(20)
    player1_pickachu1, player1_pickachu2 = (
        player1.hand_pockemon[0],
        player1.hand_pockemon[1],
    )
    player1_thunder1, player1_thunder2 = (
        player1.hand_pockemon[2],
        player1.hand_pockemon[3],
    )
    player1.prepare_active_pockemon(player1_pickachu1)
    player1.prepare_bench_pockemon(player1_pickachu2)
    player1.prepare_bench_pockemon(player1_thunder1)
    player1.prepare_bench_pockemon(player1_thunder2)
    for pockemon in [player1.active_pockemon] + player1.bench:
        pockemon.hp = 50

    assert len(player1.hand_goods) == 6
    with patch.object(player1, "select_action", return_value=44) as mock:
        player1.use_goods_select()
        # 引数のselectionのlenが18であることを確認
        assert len(mock.call_args[0][0]) == 45
        sum_hp = 0
        for pockemon in [player1.active_pockemon] + player1.bench:
            sum_hp += pockemon.hp
        assert sum_hp == 50 * 4 + 40

    # reset hp
    for pockemon in [player1.active_pockemon] + player1.bench:
        pockemon.hp = pockemon.max_hp


def test_attack_pikachu():
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

    assert player1.candidate_attack() == []

    player1.active_pockemon.attach_energy(Energy.LIGHTNING)
    player1.active_pockemon.attach_energy(Energy.LIGHTNING)

    attack_list = player1.candidate_attack()

    assert len(attack_list) == 1

    assert player2.active_pockemon.hp == player2.active_pockemon.max_hp

    player1.attack(attack_list[0])

    assert player2.active_pockemon.hp == player2.active_pockemon.max_hp - 60

    game.active_player = player2
    game.waiting_player = player1

    player2.active_pockemon.attach_energy(Energy.LIGHTNING)
    player2.active_pockemon.attach_energy(Energy.LIGHTNING)

    attack_list = player2.candidate_attack()
    assert len(attack_list) == 1

    assert player1.active_pockemon.hp == player1.active_pockemon.max_hp

    player2.attack(attack_list[0])

    assert player1.active_pockemon.hp == player1.active_pockemon.max_hp - 30

    game.active_player = player1
    game.waiting_player = player2

    player1.attack(player1_pickachu1.attacks[0])

    assert player1.sides == 2

    assert player2.active_pockemon is player2_pickachu2
    player1.attack(player1_pickachu2.attacks[0])
    with pytest.raises(GameOverException):
        player1.attack(player1_pickachu2.attacks[0])


def test_attack_shimama():
    game, player1, player2 = set_lightning()
    player1.draw(20)
    player2.draw(20)
    player1_shimama1, player1_shimama2 = (
        player1.hand_pockemon[4],
        player1.hand_pockemon[5],
    )
    player1_zeburaika1 = player1.hand_pockemon[6]
    player1.prepare_active_pockemon(player1_shimama1)
    player1.prepare_bench_pockemon(player1_shimama2)
    player2.prepare_active_pockemon(player2.hand_pockemon[0])
    player2.prepare_bench_pockemon(player2.hand_pockemon[1])
    game.active_player = player1
    game.waiting_player = player2

    player1.active_pockemon.attach_energy(Energy.LIGHTNING)
    player1.active_pockemon.attach_energy(Energy.LIGHTNING)
    player1.evolve(player1_shimama1)
    assert player1.active_pockemon is player1_zeburaika1

    with patch.object(player1, "select_action", return_value=2) as mock:
        assert player2.bench[0].hp == player2.bench[0].max_hp
        player1.attack_select()
        assert len(mock.call_args[0][0]) == 3
        assert player2.bench[0].hp == player2.bench[0].max_hp - 30


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


def test_use_trainer_select():
    game, player1, player2 = set_lightning()
    player1.draw(20)
    player2.draw(20)
    game.active_player = player1
    game.waiting_player = player2
    with patch.object(player1, "select_action", return_value=0) as mock:
        player1.use_trainer_select()
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

    with patch.object(player1, "select_action", return_value=0) as mock:
        player1.evolve_select()
        assert len(mock.call_args[0][0]) == 4

    assert player1.active_pockemon.name == "Shimama"
    assert player1.bench[0].name == "Shimama"

    with patch.object(player1, "select_action", return_value=1) as mock:
        player1.evolve_select()
        assert len(mock.call_args[0][0]) == 4
        assert player1.active_pockemon.name == "Zeburaika"
        assert player1.bench[0].name == "Shimama"


def test_retreat():
    game, player1, player2 = set_lightning()
    player1.draw(7)
    player2.draw(7)
    player1_pickachu1, player1_pickachu2 = (
        player1.hand_pockemon[0],
        player1.hand_pockemon[1],
    )
    player1_shimama1, player1_shimama2 = (
        player1.hand_pockemon[4],
        player1.hand_pockemon[5],
    )
    player1.prepare_active_pockemon(player1_shimama1)
    player1.prepare_bench_pockemon(player1_shimama2)
    player1.prepare_bench_pockemon(player1_pickachu1)
    player1.prepare_bench_pockemon(player1_pickachu2)

    game.active_player = player1
    game.waiting_player = player2

    player1_shimama1.attach_energy(Energy.LIGHTNING)

    player1.retreat(player1_shimama2, [Energy.LIGHTNING])
    assert player1.active_pockemon is player1_shimama2
    assert player1.bench[0] is player1_shimama1

    player1_shimama2.attach_energy(Energy.LIGHTNING)
    player1_shimama2.attach_energy(Energy.LIGHTNING)

    with patch.object(player1, "select_action", return_value=2) as mock:
        player1.retreat_select()
        assert len(mock.call_args[0][0]) == 4
        assert player1.active_pockemon is player1_pickachu1


def test_attack():
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
    player2.prepare_bench_pockemon(player2_pickachu2)
    game.active_player = player1
    game.waiting_player = player2

    player1.get_energy()

    player1.active_pockemon.attach_energy(Energy.LIGHTNING)
    player1.active_pockemon.attach_energy(Energy.LIGHTNING)

    attack_list = player1.candidate_attack()
    assert len(attack_list) == 1

    with patch.object(player1, "select_action", return_value=1) as mock:
        player1.attack_select()
        assert len(mock.call_args[0][0]) == 2
        assert player2.active_pockemon.hp == player2.active_pockemon.max_hp - 60


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
