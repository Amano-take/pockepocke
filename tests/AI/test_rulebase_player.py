from unittest.mock import MagicMock, patch

import pytest

from AI.rulebase_player import RuleBasePlayer
from game.deck import Deck
from game.energy import Energy
from game.game import Game
from tests.utils.set_lightning import lightning_deck, set_lightning


def create_rulebase_game():
    """Create a game with RuleBasePlayers"""
    deck = lightning_deck()
    game = Game()
    player1 = RuleBasePlayer(Deck(deck), [Energy.LIGHTNING])
    player2 = RuleBasePlayer(Deck(deck), [Energy.LIGHTNING])
    game.set_players(player1, player2)
    return game, player1, player2


def test_calculate_action_score_active_pokemon():
    """Test score calculation for active pokemon"""
    game, player, opponent = create_rulebase_game()

    # Draw cards and set up active pokemon
    player.draw(2)
    player.prepare_active_pockemon(player.hand_pockemon[0])

    # Initial score with just active pokemon
    initial_score = player.calculate_action_score()

    # Add energy to active pokemon
    player.active_pockemon.attach_energy(Energy.LIGHTNING)
    score_with_energy = player.calculate_action_score()

    # Score should increase with energy
    assert score_with_energy > initial_score


def test_calculate_action_score_bench():
    """Test score calculation for bench pokemon"""
    game, player, opponent = create_rulebase_game()

    player.draw(4)
    player.prepare_active_pockemon(player.hand_pockemon[0])
    initial_score = player.calculate_action_score()

    # Add pokemon to bench
    player.prepare_bench_pockemon(player.hand_pockemon[0])
    score_with_bench = player.calculate_action_score()

    # Score should increase with bench pokemon
    assert score_with_bench > initial_score


def test_calculate_action_score_sides():
    """Test score calculation for side cards"""
    game, player, opponent = create_rulebase_game()

    initial_score = player.calculate_action_score()
    player.sides = 2
    score_with_sides = player.calculate_action_score()

    # Score should increase with side cards
    assert score_with_sides > initial_score
    assert score_with_sides == initial_score + (2 * 30)


def test_select_action_single_choice():
    """Test select_action when there's only one choice"""
    game, player, opponent = create_rulebase_game()

    selection = {0: "Only choice"}
    result = player.select_action(selection)
    assert result == 0


def test_select_action_multiple_choices():
    """Test select_action when there are multiple choices"""
    game, player, opponent = create_rulebase_game()

    # Mock actions that would result in different scores
    def action1():
        player.sides = 1  # Lower score action

    def action2():
        player.sides = 2  # Higher score action

    selection = {0: "Choice 1", 1: "Choice 2"}
    actions = {0: action1, 1: action2}

    result = player.select_action(selection, actions)
    assert result == 1  # Should choose action with higher score


def test_select_action_with_opponent():
    """Test select_action considering opponent's state"""
    game, player, opponent = create_rulebase_game()

    player.draw(2)
    opponent.draw(2)

    # Set up active pokemon for both players
    player.prepare_active_pockemon(player.hand_pockemon[0])
    opponent.prepare_active_pockemon(opponent.hand_pockemon[0])

    # Mock actions
    def action1():
        opponent.active_pockemon.hp -= 30  # Better action

    def action2():
        opponent.active_pockemon.hp -= 10

    selection = {0: "Attack 1", 1: "Attack 2"}
    actions = {0: action1, 1: action2}

    result = player.select_action(selection, actions)
    assert result == 0  # Should choose action that deals more damage
