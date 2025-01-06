import pytest
from unittest.mock import patch
from game.cards import *

from game.deck import Deck
from game.player import Player
from game.energy import Energy
from game.game import Game

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
    selevi_player1 = Selevi(player1)
    selevi_player2 = Selevi(player2)

    selevi_player1.attach_energy(Energy.GRASS)
    selevi_player2.attach_energy(Energy.GRASS)

    assert selevi_player1.attacks[0].can_attack() == False
    assert selevi_player2.attacks[0].can_attack() == False

    player1.energy_values[Energy.GRASS.value] = 2

    assert selevi_player1.attacks[0].can_attack() == True
    assert selevi_player2.attacks[0].can_attack() == False


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

    assert player1.active_pockemon.hp == player1.active_pockemon.max_hp


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
