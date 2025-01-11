from random import random
from enum import Enum

from game.player import Player
from game.exceptions import GameOverException


class Game:
    def __init__(self):
        self.turn = 0
        self.winner = None
        self.loser = None

    def set_players(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.player1.set_game(self)
        self.player2.set_game(self)
        self.active_player = None
        self.waiting_player = None

    def start(self):
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
        while True:
            self.turn += 1
            self.active_player.draw()
            if self.turn > 1:
                self.active_player.get_energy()
            can_attack = self.turn > 1
            can_evolve = self.turn > 2
            try:
                self.active_player.start_turn(can_attack, can_evolve)
            except GameOverException as e:
                print(e)
                break

            self.active_player, self.waiting_player = (
                self.waiting_player,
                self.active_player,
            )

    def coin_toss(self):
        # 0が外れ　1が当たり
        return random() < 0.5
