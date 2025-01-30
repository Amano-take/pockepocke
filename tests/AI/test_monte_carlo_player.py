import pytest
from unittest.mock import MagicMock, patch
from AI.monte_carlo_player import MonteCarloPlayer
from game.deck import Deck
from game.energy import Energy
from game.game import Game
from tests.utils.set_lightning import lightning_deck, set_lightning

# set random seed
import random
random.seed(0)

def create_monte_carlo_game():
    """Create a game with MonteCarloPlayers"""
    deck = lightning_deck()
    game = Game()
    player1 = MonteCarloPlayer(Deck(deck), [Energy.LIGHTNING], n_simulations=10)
    player2 = MonteCarloPlayer(Deck(deck), [Energy.LIGHTNING], n_simulations=10)
    game.set_players(player1, player2)
    return game, player1, player2

def test_monte_carlo_initialization():
    """Test MonteCarloPlayer initialization"""
    game, player1, player2 = create_monte_carlo_game()
    assert player1.n_simulations == 10
    assert isinstance(player1, MonteCarloPlayer)
    assert player1.energy_candidates == [Energy.LIGHTNING]

def test_monte_carlo_select_action1():
    game, player1, player2 = create_monte_carlo_game()
    selection = {0: "[pockemon] ポケモンを場に出す"}
    action = {0: lambda: None}
    assert player1.select_action(selection, action) == 0

def test_monte_carlo_select_action2():
    game, player1, player2 = create_monte_carlo_game()
    player1.draw(7)
    player2.draw(7)
    assert player1.hand_pockemon[0].name == "PikachuEX"
    assert player2.hand_pockemon[0].name == "PikachuEX"

	# assert not raise error
    player1.pockemon_active_select()
