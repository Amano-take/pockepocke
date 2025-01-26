import copy
import logging
import os
import pickle
import random
from typing import Callable, Dict, List, Tuple

from game.game import Game
from game.player import Player

logger = logging.getLogger(__name__)


class MonteCarloPlayer(Player):
    def __init__(self, deck, energy_types, n_simulations=100):
        super().__init__(deck, energy_types)
        self.n_simulations = n_simulations

    def select_action(
        self, selection: Dict[int, str], action: Dict[int, Callable] = {}
    ) -> int:
        """Monte Carlo simulationによる行動選択"""
        if len(selection) == 1:
            return 0

        phase = str()  # TODO

        # 各行動の評価値を計算
        scores = self.evaluate_actions(selection, action, phase)

        logger.debug(f"scores: {scores}")
        logger.debug(f"selection: {selection}")

        # 最も評価値の高い行動を選択
        best_action = max(scores.items(), key=lambda x: x[1])[0]
        logger.debug(f"selected action: {best_action}")

        return best_action

    # 通常ターンの行動
    def start_turn(self, phase: str = "goods", can_evolve: bool = True):
        phases = [
            "goods",
            "trainer",
            "evolve",
            "pockemon",
            "energy",
            "feature",
            "retreat",
            "attack",
        ]
        index = phases.index(phase)
        if index == 0:
            # goodsを使う
            self.use_goods()
        if index <= 1:
            # trainerを使う
            self.use_trainer()
        if index <= 2:
            # 手札のポケモンを進化させる
            self.evolve_select(can_evolve=can_evolve)
        if index <= 3:
            # 手札のポケモンを出す
            self.use_pockemon_select()
        if index <= 4:
            # エネルギーをつける
            self.attach_energy_select()
        if index <= 5:
            # 特性を使う　# TODO: 対象指定が必要な特性
            self.use_feature_select()
        if index <= 6:
            # 逃げる
            self.retreat_select()
        if index <= 7:
            # 攻撃する
            self.attack_select()
        if index <= 8:
            # ターン終了する
            self.end_turn()
        return

    def evaluate_actions(
        self, selection: Dict[int, str], action: Dict[int, Callable], phase: str
    ) -> Dict[int, float]:
        """各行動の評価値を計算"""
        scores = {key: 0.0 for key in selection.keys()}
        self.save_pkl()
        self.opponent.save_pkl()

        for action_key in selection.keys():
            self.opponent.set_random()

            # n_simulations回のシミュレーションを実行
            total_score = 0.0
            for _ in range(self.n_simulations):
                # 状態をコピー
                # 行動を実行
                action[action_key]()
                game_copy = copy.deepcopy(self.game)

                # シミュレーション実行
                score = self.simulate_game(game_copy, phase)
                total_score += score

            # 平均スコアを計算
            scores[action_key] = total_score / self.n_simulations

            # 元の状態に戻す
            self.load_pkl()

        self.delete_pkl()
        self.opponent.delete_pkl()

        return scores

    def simulate_game(self, game: Game, phase: str) -> float:
        """ゲームをシミュレート"""
        max_turn = 30
        winner_name = game.simulate(phase)
        if winner_name is None:
            # 引き分け
            return 0.5
        elif winner_name == self.name:
            return 1.0
        else:
            return 0.0

    def evaluate_state(self, player: Player, opponent: Player) -> float:
        """現在の状態を評価"""
        # サイド状況による評価
        if player.sides == 0:
            return 0.0  # 敗北
        elif opponent.sides == 0:
            return 1.0  # 勝利

        # その他の状態を評価
        score = 0.5  # ベースライン

        # サイドカードの比率
        score += 0.3 * (player.sides / 6)
        score -= 0.3 * (opponent.sides / 6)

        # アクティブポケモンのHP比率
        if player.active_pockemon:
            score += 0.2 * (player.active_pockemon.hp / player.active_pockemon.max_hp)
        if opponent.active_pockemon:
            score -= 0.2 * (
                opponent.active_pockemon.hp / opponent.active_pockemon.max_hp
            )

        return score
