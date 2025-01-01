import pytest
from unittest.mock import patch
from game.cards.pockemon_cards.grass_cards import (
    TamaTama,
    Nassy,
    Selevi,
    Tsutaja,
    Janobii,
    Jaroda,
    Nemashu,
    Masheedo,
    Dadarin,
)
from game.deck import Deck
from game.player import Player
from game.energy import Energy


def test_prepare():
    deck = [TamaTama(), Nassy(), Selevi()]
    for _ in range(17):
        deck.append(Tsutaja())

    player = Player(Deck(deck), [Energy.GRASS])
    player.deck.init_deck()
    player.draw(5)

    with patch.object(player, "select_action", return_value=0) as mock:
        player.prepare()
        mock.assert_called_once()


def _test_prepare():
    deck = [TamaTama(), Nassy(), Selevi()]
    for _ in range(17):
        deck.append(Tsutaja())

    player = Player(Deck(deck), [Energy.GRASS])
    player.deck.init_deck()
    player.draw(5)
    player.prepare()


if __name__ == "__main__":
    _test_prepare()
    print("test_prepare passed")
