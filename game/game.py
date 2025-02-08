import logging
import os
import pickle
import uuid
from enum import Enum
from random import random

from game.exceptions import GameOverException
from game.player import Player


class Game:
    max_turn = 30

    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.active_player = None
        self.waiting_player = None
        self.turn = 0
        self.winner = None
        self.is_active = False
        self.game_id = str(uuid.uuid4())
        self.logger = logging.getLogger(__name__)

    def set_level(self, level: int):
        """ロガーのログレベルを設定する"""
        self.logger.setLevel(level)

    def set_players(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.player1.set_game(self)
        self.player2.set_game(self)
        self.active_player = player2
        self.waiting_player = player1

    def shuffle_deck(self):
        self.player1.deck.shuffle()
        self.player2.deck.shuffle()

    def start(self):
        try:
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
        except Exception as e:
            self.logger.error(f"ゲーム開始中にエラーが発生: {str(e)}")
            self.is_active = False
            raise

    def turn_start(self):
        try:
            while self.turn < self.max_turn:
                self.logger.info(f"ターン: {self.turn}")
                self.turn += 1
                self.active_player.draw()
                if self.turn > 1:
                    self.active_player.get_energy()
                can_evolve = self.turn > 2
                try:
                    self.active_player.start_turn(can_evolve=can_evolve)
                except GameOverException as e:
                    self.winner = e.winner
                    break

                self.active_player, self.waiting_player = (
                    self.waiting_player,
                    self.active_player,
                )
            self.is_active = False
        except Exception as e:
            self.logger.error(f"ターン処理中にエラーが発生: {str(e)}")
            self.is_active = False
            raise

    def get_player_by_name(self, name: str):
        if self.player1.name == name:
            return self.player1
        if self.player2.name == name:
            return self.player2
        raise ValueError("プレイヤーが見つかりません")

    def coin_toss(self):
        # 0が外れ　1が当たり
        return random() < 0.5

    def simulate_with_rulebase(
        self, phase: str = "goods", name: str = "RuleBasePlayer"
    ):
        from AI.rulebase_player import RuleBasePlayer

        play_out_player = (
            self.active_player
            if name == self.active_player.name
            else self.waiting_player
        )
        other_player = (
            self.active_player
            if name == self.waiting_player.name
            else self.waiting_player
        )

        assert isinstance(play_out_player, RuleBasePlayer)
        assert isinstance(other_player, RuleBasePlayer)

        play_out_player.unset_random()
        other_player.unset_random()

        # prepare phaseの場合
        if phase == "select_active":
            assert False
            play_out_player.prepare(phase)
        elif phase == "select_bench":
            play_out_player.prepare(phase)
            other_player.prepare()
        elif phase == "goods":
            if other_player.active_pockemon.name == "PockemonCard":
                other_player.prepare()
        else:
            assert play_out_player is self.active_player
            can_evolve = self.turn > 2
            play_out_player.start_turn(phase=phase, can_evolve=can_evolve)
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
                self.winner = e.winner
                break
            self.active_player, self.waiting_player = (
                self.waiting_player,
                self.active_player,
            )

        self.is_active = False
        return self.winner

    def simulate(self, phase: str = "goods", name: str = "MonteCarloPlayer"):
        from AI.monte_carlo_player import MonteCarloPlayer

        play_out_player = (
            self.active_player
            if name == self.active_player.name
            else self.waiting_player
        )
        other_player = (
            self.active_player
            if name == self.waiting_player.name
            else self.waiting_player
        )

        assert isinstance(play_out_player, MonteCarloPlayer)
        assert self.active_player.is_random and self.waiting_player.is_random

        # prepare phaseの場合
        if phase == "select_active":
            assert False
            play_out_player.prepare(phase)
        elif phase == "select_bench":
            play_out_player.prepare(phase)
            other_player.prepare()
        elif phase == "goods":
            if other_player.active_pockemon.name == "PockemonCard":
                other_player.prepare()
        else:
            assert play_out_player is self.active_player
            can_evolve = self.turn > 2
            play_out_player.start_turn(phase=phase, can_evolve=can_evolve)
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
                self.winner = e.winner
                break
            self.active_player, self.waiting_player = (
                self.waiting_player,
                self.active_player,
            )

        self.is_active = False
        return self.winner

    def save_pkl(self):
        with open(f"data/game/{self.game_id}.pkl", "wb") as f:
            pickle.dump(self, f)

    def load_pkl(self):
        with open(f"data/game/{self.game_id}.pkl", "rb") as f:
            game = pickle.load(f)
        assert game.game_id == self.game_id
        # load self
        for key, value in game.__dict__.items():
            if isinstance(value, Player):
                pass
            else:
                self.__dict__[key] = value

        return self

    def delete_pkl(self):
        os.remove(f"data/game/{self.game_id}.pkl")

    def is_finished(self) -> bool:
        """ゲームが終了しているかどうかを判定"""
        return (
            not self.is_active or self.winner is not None or self.turn >= self.max_turn
        )

    def next_turn(self):
        """次のターンに進む"""
        self.active_player, self.waiting_player = (
            self.waiting_player,
            self.active_player,
        )
        self.turn += 1

    def replace_player(self, player: Player, new_player: Player):
        if player == self.player1:
            self.player1 = new_player
        elif player == self.player2:
            self.player2 = new_player
        else:
            raise ValueError("プレイヤーが見つかりません")

        if self.active_player == player:
            self.active_player = new_player
        elif self.waiting_player == player:
            self.waiting_player = new_player
        else:
            raise ValueError("プレイヤーが見つかりません")

    def set_logger(self, loglevel):
        self.player1.set_logger(loglevel)
        self.player2.set_logger(loglevel)
