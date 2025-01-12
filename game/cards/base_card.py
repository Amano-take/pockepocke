from __future__ import annotations


class Card:
    def __init__():
        pass

    def set_player(self, player: Player, opponent: Player):
        self.player = player
        self.opponent = opponent

    def set_game(self, game: Game):
        self.game = game


if __name__ == "__main__":
    from game.player import Player
    from game.game import Game
