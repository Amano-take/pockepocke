from random import random


from game.player import Player
from enum import Enum


class Game:
    def __init__(self):
        self.player1 = Player()
        self.player2 = Player()
        self.turn = 0
        self.winner = None
        self.loser = None

        # コイントスで先攻後攻を決める
        if random() < 0.5:
            self.active_player = self.player1
            self.waiting_player = self.player2
        else:
            self.active_player = self.player2
            self.waiting_player = self.player1

        # 準備フェーズ
        self.player1.deck.init_deck()
        self.player2.deck.init_deck()
        self.player1.draw(5)
        self.player2.draw(5)
        self.player1.prepare()
        self.player2.prepare()

        # ターン開始
        self.turn_start()

    def turn_start(self):
        self.turn += 1
        self.active_player.draw()
        if self.turn > 1:
            self.active_player.get_energy()
        self.active_player.start_turn()
