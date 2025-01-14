from __future__ import annotations
from uuid import uuid4


class Card:
    def __init__(self):
        self.id_ = uuid4()

    def __eq__(self, other: Card):
        return self.id_ == other.id_

    def set_player(self, player: Player, opponent: Player):
        self.player = player
        self.opponent = opponent

    def set_game(self, game: Game):
        self.game = game


if __name__ == "__main__":
    from game.player import Player
    from game.game import Game
