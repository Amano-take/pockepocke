from __future__ import annotations


class GameOverException(Exception):
    def __init__(self, winner: Player):
        self.winner = winner
        super().__init__(f"{winner.name}の勝ち")


if __name__ == "__main__":
    from game.player import Player
