import pytest
from unittest.mock import patch
from game.cards import *

from game.deck import Deck
from game.player import Player
from game.energy import Energy
from game.game import Game

game = Game()

deck = [
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

player1 = Player(Deck(deck), [Energy.LIGHTNING])
player2 = Player(Deck(deck), [Energy.LIGHTNING])

game.set_players(player1, player2)


def test_attack_pikachu():
	pass


