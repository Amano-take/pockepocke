# set random seed
import random
from unittest.mock import MagicMock, patch

import pytest

from AI.monte_carlo_player import MonteCarloPlayer
from game.deck import Deck
from game.energy import Energy
from game.exceptions import GameOverException
from game.game import Game
from tests.utils.set_lightning import lightning_deck, set_lightning

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


def test_monte_carlo_select_action3():
    game, player1, player2 = create_monte_carlo_game()
    player1.draw(7)
    player2.draw(7)
    pikachu_ex = player1.hand_pockemon[0]
    player1.prepare_active_pockemon(pikachu_ex)
    assert player1.active_pockemon == pikachu_ex

    # assert not raise error
    player1.pockemon_bench_select()


# def test_monte_carlo_select_action4():
#     game, player1, player2 = create_monte_carlo_game()
#     player1.n_simulations = 1
#     player2.n_simulations = 1
#     game.start()


def test_monte_carlo_simulation():
    game, player1, player2 = create_monte_carlo_game()
    player1.draw(7)
    player2.draw(1)

    player1.prepare_active_pockemon(player1.hand_pockemon[3])
    player2.prepare_active_pockemon(player2.hand_pockemon[0])

    game.active_player = player1
    game.waiting_player = player2

    player2.active_pockemon.get_damage(game, 110)

    player1.active_pockemon.attach_energy(Energy.LIGHTNING)

    # GameOverExceptionが発生することを確認
    with pytest.raises(GameOverException):
        player1.attack_select()


def debug_playout():
    game, player1, player2 = create_monte_carlo_game()
    player1.draw(7)
    player2.draw(2)

    player1.prepare_active_pockemon(player1.hand_pockemon[3])
    player2.prepare_active_pockemon(player2.hand_pockemon[0])

    player1.active_pockemon.attach_energy(Energy.LIGHTNING)

    game.active_player = player1
    game.waiting_player = player2
    player1.set_random()
    player2.set_random()

    player2.active_pockemon.get_damage(game, 50)

    from interface.visualizer import Visualizer
    import threading

    vis = Visualizer()
    vis.set_game(game)
    thread1 = threading.Thread(target=vis.visualize, daemon=True)

    winner = None

    def simulate_game():
        player1.save_pkl()
        player2.save_pkl()
        player1.simulate_game_with_rulebase(game, "goods")

    thread2 = threading.Thread(target=simulate_game, daemon=True)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # get thread2 result
    assert game.winner is not None
