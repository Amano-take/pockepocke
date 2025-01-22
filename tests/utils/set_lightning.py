from unittest.mock import patch

import pytest

from game.cards import *
from game.deck import Deck
from game.energy import Energy
from game.exceptions import GameOverException
from game.game import Game
from game.player import Player


def set_lightning():
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

    return game, player1, player2


def lightning_deck():
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

    return deck_lightning
