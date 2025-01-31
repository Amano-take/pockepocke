import copy
import logging
import random
from typing import Callable, Dict, List, Tuple

from game.exceptions import GameOverException
from game.game import Game
from game.player import Player

logger = logging.getLogger(__name__)


class MonteCarloPlayer(Player):
    def __init__(self, deck, energy_types, n_simulations=100):
        super().__init__(deck, energy_types)
        self.n_simulations = n_simulations
        # save log to file
        log_path = f"data/log/monte_carlo_player_{self.name}.txt"
        logger.addHandler(logging.FileHandler(log_path))
        logger.setLevel(logging.DEBUG)
        logger.debug(f"Monte Carlo Player {self.name} initialized")

    def select_action(
        self, selection: Dict[int, str], action: Dict[int, Callable] = {}
    ) -> int:
        """Monte Carlo simulationによる行動選択"""
        if len(selection) == 1:
            return 0

        # selectionの最初の値から[...]の中身を抽出
        first_selection = selection[0]
        phase = first_selection[
            first_selection.find("[") + 1 : first_selection.find("]")
        ]

        if phase == "opponent_trainer":
            # TODO: 相手のトレーナーに対して、どのカードを選択するか決めるところ。ターンのactive_playerは相手。
            return 0
        next_phase = self.get_next_phase(phase)

        if self.is_random:
            if phase == "select_energy":
                return 1
            elif phase == "select_retreat":
                return 0
            elif phase == "attack":
                return max(selection.keys())
            else:
                return random.randint(0, len(selection) - 1)

        # 各行動の評価値を計算
        scores = self.evaluate_actions(selection, action, next_phase)

        logger.debug(f"scores: {scores}")
        logger.debug(f"selection: {selection}")

        # 最も評価値の高い行動を選択
        best_action = max(scores.items(), key=lambda x: x[1])[0]
        logger.debug(f"selected action: {best_action}")

        return best_action

    def prepare(self, phase: str = "select_active"):
        if phase == "select_active":
            self.pockemon_active_select()
            self.pockemon_bench_select()
        elif phase == "select_bench":
            self.pockemon_bench_select()
        else:
            raise ValueError(f"Invalid phase: {phase}")

    def get_next_phase(self, phase: str) -> str:
        if phase == "select_active":
            return "select_bench"
        elif phase == "select_bench":
            return "goods"
        elif phase == "attack":
            return "goods"
        phases = [
            "goods",
            "trainer",
            "evolve",
            "pockemon",
            "select_energy",
            "feature",
            "select_retreat",
            "attack",
        ]
        return phases[phases.index(phase) + 1]

    # 通常ターンの行動
    def start_turn(self, phase: str = "goods", can_evolve: bool = True):
        phases = [
            "goods",
            "trainer",
            "evolve",
            "pockemon",
            "select_energy",
            "feature",
            "select_retreat",
            "attack",
        ]
        index = phases.index(phase)
        if index == 0:
            # goodsを使う
            self.use_goods_select()
        if index <= 1:
            # trainerを使う
            self.use_trainer_select()
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
            self.set_random()

            # n_simulations回のシミュレーションを実行
            total_score = 0.0
            try:
                action[action_key]()
            except GameOverException as e:
                if e.winner == self.opponent:
                    scores[action_key] = -float("inf")
                else:
                    scores[action_key] = float("inf")
                continue
            for _ in range(self.n_simulations):
                # 状態をコピー
                # 行動を実行
                game_copy = copy.deepcopy(self.game)

                # シミュレーション実行
                score = self.simulate_game(game_copy, phase, name=self.name)
                total_score += score

            # 平均スコアを計算
            scores[action_key] = total_score / self.n_simulations

            # 元の状態に戻す
            self.load_pkl()
            self.opponent.load_pkl()

        self.delete_pkl()
        self.opponent.delete_pkl()

        return scores

    def simulate_game(self, game: Game, phase: str, name: str) -> float:
        """ゲームをシミュレート"""
        max_turn = 30
        winner_player = game.simulate(phase, name)
        if winner_player is None:
            # 引き分け
            return 0.5
        elif winner_player.name == self.name:
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
