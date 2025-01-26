from enum import Enum
from random import random

from game.exceptions import GameOverException
from game.player import Player


class Game:
    max_turn = 30

    def __init__(self):
        self.turn = 0
        self.winner: Player | None = None
        self.loser: Player | None = None
        self.is_active = False

    def set_players(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.player1.set_game(self)
        self.player2.set_game(self)
        self.active_player = player2
        self.waiting_player = player1

    def start(self):
        # コイントスで先攻後攻を決める
        self.is_active = True
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
            can_evolve = self.turn > 2
            try:
                self.active_player.start_turn(can_evolve=can_evolve)
            except GameOverException as e:
                print(e)
                break

            self.active_player, self.waiting_player = (
                self.waiting_player,
                self.active_player,
            )
        self.is_active = False

    def get_player_by_name(self, name: str):
        if self.player1.name == name:
            return self.player1
        if self.player2.name == name:
            return self.player2
        raise ValueError("プレイヤーが見つかりません")

    def coin_toss(self):
        # 0が外れ　1が当たり
        return random() < 0.5

    def simulate(self, phase: str = "goods"):
        from AI.monte_carlo_player import MonteCarloPlayer

        assert isinstance(self.active_player, MonteCarloPlayer)
        assert isinstance(self.waiting_player, Player)
        assert self.active_player.is_random and self.waiting_player.is_random

        can_evolve = self.turn > 2
        self.active_player.start_turn(phase=phase, can_evolve=can_evolve)
        self.active_player, self.waiting_player = (
            self.waiting_player,
            self.active_player,
        )

        while self.turn < self.max_turn:
            self.turn += 1
            self.active_player.draw()
            if self.turn > 1:
                self.active_player.get_energy()
            can_evolve = self.turn > 2
            try:
                self.active_player.start_turn(can_evolve=can_evolve)
            except GameOverException as e:
                break
            self.active_player, self.waiting_player = (
                self.waiting_player,
                self.active_player,
            )

        self.is_active = False
        return self.winner

    def is_finished(self) -> bool:
        """ゲームが終了しているかどうかを判定"""
        return not self.is_active or self.winner is not None or self.turn >= self.max_turn

    def next_turn(self):
        """次のターンに進む"""
        self.active_player, self.waiting_player = self.waiting_player, self.active_player
        self.turn += 1
