from unittest.mock import patch

import pytest

from game.cards.pockemon_card import PockemonCard
from game.cards.trainer_cards.trainers import HakaseResearcher
from game.game import Game
from game.player import Player
from tests.utils.set_lightning import set_lightning


def test_hakase_researcher():
    game, player1, player2 = set_lightning()
    initial_hand_count = 11
    player1.draw(initial_hand_count)  # Draw initial card

    game.active_player = player1
    game.waiting_player = player2

    with patch.object(player1, "select_action", return_value=1):
        player1.use_trainer_select()

    assert (
        len(player1.hand_goods) + len(player1.hand_pockemon) + len(player1.hand_trainer)
        == initial_hand_count + 1
    ), "HakaseResearcher should add 2 cards to the hand"

    assert len(player1.trash) == 1, "HakaseResearcher should add 1 card to the trash"


if __name__ == "__main__":
    pytest.main()
