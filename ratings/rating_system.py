from dataclasses import dataclass
import math
from typing import Tuple


@dataclass
class EloRating:
    """Eloレーティングシステムの実装"""

    k_factor: float = 32.0  # レーティング変動の大きさを制御
    initial_rating: float = 1500.0  # 初期レーティング
    min_rating: float = 1000.0  # 最小レーティング
    max_rating: float = 2000.0  # 最大レーティング

    def calculate_expected_score(self, rating1: float, rating2: float) -> float:
        """期待勝率を計算

        Args:
            rating1: プレイヤー1のレーティング
            rating2: プレイヤー2のレーティング

        Returns:
            プレイヤー1の期待勝率（0-1の値）
        """
        return 1 / (1 + math.pow(10, (rating2 - rating1) / 400))

    def calculate_new_ratings(
        self, rating1: float, rating2: float, result: float
    ) -> Tuple[float, float]:
        """新しいレーティングを計算

        Args:
            rating1: プレイヤー1のレーティング
            rating2: プレイヤー2のレーティング
            result: 対戦結果（1=勝利, 0.5=引き分け, 0=敗北）

        Returns:
            (プレイヤー1の新レーティング, プレイヤー2の新レーティング)
        """
        expected1 = self.calculate_expected_score(rating1, rating2)
        expected2 = 1 - expected1  # プレイヤー2の期待勝率

        # レーティングの変動値を計算（K係数は両者で同じ）
        change1 = self.k_factor * (result - expected1)
        change2 = self.k_factor * ((1 - result) - expected2)

        # 新しいレーティングを計算（最小値と最大値で制限）
        new_rating1 = max(self.min_rating, min(self.max_rating, rating1 + change1))
        new_rating2 = max(self.min_rating, min(self.max_rating, rating2 + change2))

        return new_rating1, new_rating2

    def scale_to_display_score(self, rating: float) -> float:
        """レーティングを0-100のスケールに変換

        Args:
            rating: 元のレーティング（1000-2000）

        Returns:
            0-100のスケールに変換されたスコア
        """
        normalized = (rating - self.min_rating) / (self.max_rating - self.min_rating)
        return max(0, min(100, normalized * 100))

    def get_confidence_level(self, games_played: int) -> float:
        """信頼度スコアを計算

        Args:
            games_played: プレイ済みゲーム数

        Returns:
            0-100の信頼度スコア
        """
        if games_played >= 10:
            return 100.0
        return games_played * 10.0


if __name__ == "__main__":
    # 使用例
    elo = EloRating()

    # 同じレーティングの場合
    rating1, rating2 = 1500, 1500
    expected = elo.calculate_expected_score(rating1, rating2)
    print(f"Expected score for equal ratings: {expected:.2f}")  # Should be close to 0.5

    # プレイヤー1が勝利した場合
    new_rating1, new_rating2 = elo.calculate_new_ratings(rating1, rating2, 1)
    print(f"After player 1 wins: {new_rating1:.0f} vs {new_rating2:.0f}")

    # スケーリングのテスト
    print(
        f"Display score for 1500: {elo.scale_to_display_score(1500):.0f}"
    )  # Should be 50
    print(
        f"Display score for 2000: {elo.scale_to_display_score(2000):.0f}"
    )  # Should be 100
    print(
        f"Display score for 1000: {elo.scale_to_display_score(1000):.0f}"
    )  # Should be 0
