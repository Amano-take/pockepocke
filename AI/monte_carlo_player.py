from game.player import Player
from game.game import Game
import logging
import pickle
import random
from typing import Dict, Callable, Tuple, List
import copy

logger = logging.getLogger(__name__)


class MonteCarloPlayer(Player):
    def __init__(self, deck, energy_types, n_simulations=100, simulation_depth=10):
        super().__init__(deck, energy_types)
        self.n_simulations = n_simulations
        self.simulation_depth = simulation_depth

    def select_action(
        self, selection: Dict[int, str], action: Dict[int, Callable] = {}
    ) -> int:
        """Monte Carlo simulationによる行動選択"""
        if len(selection) == 1:
            return 0

        # 現在の状態を保存
        with open("./player.pkl", "wb") as f:
            pickle.dump(self, f)

        # 各行動の評価値を計算
        scores = self.evaluate_actions(selection, action)

        logger.debug(f"scores: {scores}")
        logger.debug(f"selection: {selection}")

        # 最も評価値の高い行動を選択
        best_action = max(scores.items(), key=lambda x: x[1])[0]
        logger.debug(f"selected action: {best_action}")

        # 元の状態に戻す
        self.load_pkl()

        return best_action

    def evaluate_actions(
        self, selection: Dict[int, str], action: Dict[int, Callable]
    ) -> Dict[int, float]:
        """各行動の評価値を計算"""
        scores = {key: 0.0 for key in selection.keys()}

        for action_key in selection.keys():
            # 行動を実行
            # TODO: 相手の行動が必要なactionの場合バグの発生
            # TODO:
            action[action_key]()

            # n_simulations回のシミュレーションを実行
            total_score = 0.0
            for _ in range(self.n_simulations):
                # 状態をコピー
                game_copy = copy.deepcopy(self.game)
                player_copy = copy.deepcopy(self)
                opponent_copy = copy.deepcopy(self.opponent)

                # シミュレーション実行
                score = self.simulate_game(game_copy, player_copy, opponent_copy)
                total_score += score

            # 平均スコアを計算
            scores[action_key] = total_score / self.n_simulations

            # 元の状態に戻す
            self.load_pkl()

        return scores

    def simulate_game(self, game: Game, player: Player, opponent: Player) -> float:
        """ゲームをシミュレート"""
        for _ in range(self.simulation_depth):
            # ゲーム終了判定
            if player.sides == 0:  # 敗北
                return 0.0
            elif opponent.sides == 0:  # 勝利
                return 1.0

            # ランダムな行動を選択
            try:
                selection = {}  # TODO: 現在の選択可能な行動を取得
                action = random.choice(list(selection.keys()))
                # TODO: 行動を実行
            except Exception:
                # エラーが発生した場合は中間的な評価値を返す
                break

        # シミュレーション終了時の評価
        return self.evaluate_state(player, opponent)

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

    def load_pkl(self):
        """状態を復元"""
        with open("./player.pkl", "rb") as f:
            loaded_obj = pickle.load(f)
            for key, value in loaded_obj.__dict__.items():
                current_attr = getattr(self, key, None)
                if isinstance(current_attr, list) and isinstance(value, list):
                    current_attr.clear()
                    current_attr.extend(value)
                elif isinstance(current_attr, dict) and isinstance(value, dict):
                    current_attr.clear()
                    current_attr.update(value)
                elif isinstance(current_attr, Game):
                    pass
                elif isinstance(current_attr, Player):
                    pass
                else:
                    setattr(self, key, value)
