import asyncio
import logging
import random
from typing import List, Optional, Tuple
from pathlib import Path
import sys
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).resolve().parents[1]))

from server.database import (
    get_decks_by_client_id,
    update_deck_rating,
    get_all_client_ids,
)
from ratings.deck_evaluator import DeckEvaluator, DeckEvaluation

logger = logging.getLogger(__name__)


class SimulationManager:
    """デッキ評価シミュレーションを管理するクラス"""

    def __init__(self):
        self.evaluator = DeckEvaluator()
        self._running = False
        self._evaluation_task: Optional[asyncio.Task] = None
        self.evaluation_interval = 60  # 評価間隔（秒）
        self.matches_per_evaluation = 5  # 1回の評価で行うマッチ数

    async def start_continuous_evaluation(self):
        """継続的な評価プロセスを開始"""
        if self._running:
            return

        self._running = True
        self._evaluation_task = asyncio.create_task(self._continuous_evaluation_loop())
        logger.info("継続的な評価プロセスを開始しました")

    async def stop_evaluation(self):
        """評価プロセスを停止"""
        self._running = False
        if self._evaluation_task:
            self._evaluation_task.cancel()
            try:
                await self._evaluation_task
            except asyncio.CancelledError:
                pass
        logger.info("評価プロセスを停止しました")

    async def _continuous_evaluation_loop(self):
        """継続的な評価ループ"""
        while self._running:
            try:
                # ランダムにマッチを設定して評価
                for _ in range(self.matches_per_evaluation):
                    # すべてのデッキを取得（毎回最新の情報を取得）
                    all_decks = []
                    client_ids = await self._get_all_client_ids()
                    for client_id in client_ids:
                        decks = await asyncio.to_thread(
                            get_decks_by_client_id, client_id
                        )
                        all_decks.extend(decks)

                    if len(all_decks) < 2:
                        continue

                    # 評価対象のデッキをランダムに2つ選択
                    deck1, deck2 = random.sample(all_decks, 2)

                    # 最後の更新から一定時間経過したデッキを優先
                    time_threshold = datetime.now() - timedelta(hours=1)
                    last_updated1 = deck1.get("last_updated", "2000-01-01T00:00:00")
                    last_updated2 = deck2.get("last_updated", "2000-01-01T00:00:00")

                    if isinstance(last_updated1, str) and isinstance(
                        last_updated2, str
                    ):
                        try:
                            if (
                                datetime.fromisoformat(last_updated1) > time_threshold
                                and datetime.fromisoformat(last_updated2)
                                > time_threshold
                            ):
                                continue
                        except ValueError:
                            # 日付の解析に失敗した場合は古いとみなして続行
                            pass

                    # 対戦を実行
                    logger.info(
                        f"対戦開始: Deck1(ID:{deck1['id']}, Rating:{float(deck1['rating']):.1f}, 勝率:{int(deck1['wins'])}/{int(deck1['games_played'])}) vs "
                        f"Deck2(ID:{deck2['id']}, Rating:{float(deck2['rating']):.1f}, 勝率:{int(deck2['wins'])}/{int(deck2['games_played'])})"
                    )
                    result = await self.evaluator.evaluate_match(
                        deck1["id"],
                        deck1["cards"],
                        deck1["energy"],
                        deck2["id"],
                        deck2["cards"],
                        deck2["energy"],
                    )
                    logger.info(
                        f"対戦結果: {'Deck1の勝利' if result else 'Deck2の勝利'}"
                    )

                    # データベースから最新の情報を取得して表示
                    client_ids = await self._get_all_client_ids()
                    deck1_data = None
                    deck2_data = None

                    for client_id in client_ids:
                        decks = await asyncio.to_thread(
                            get_decks_by_client_id, client_id
                        )
                        for deck in decks:
                            if deck["id"] == deck1["id"]:
                                deck1_data = deck
                            if deck["id"] == deck2["id"]:
                                deck2_data = deck
                        if deck1_data and deck2_data:
                            break

                    if deck1_data and deck2_data:
                        logger.info(
                            f"新レーティング - Deck1: {float(deck1_data['rating']):.1f} ({int(deck1_data['wins'])}/{int(deck1_data['games_played'])}), "
                            f"Deck2: {float(deck2_data['rating']):.1f} ({int(deck2_data['wins'])}/{int(deck2_data['games_played'])})"
                        )

            except Exception as e:
                logger.error(f"評価プロセス中にエラーが発生: {e}")

            await asyncio.sleep(self.evaluation_interval)

    async def _get_all_client_ids(self) -> List[str]:
        """すべてのクライアントIDを取得"""
        return await asyncio.to_thread(get_all_client_ids)

    async def _update_reference_score(self, deck_id: int):
        """デッキの参考度合いを更新（-100から+100の範囲）

        レーティングの下限から上限を示す形で計算：
        1. 対戦回数による信頼性（0-40点）
        2. レーティングの範囲（-60-+60点）
            - 1000未満: -60点
            - 1000-2000: 比例配分
            - 2000以上: +60点
        """
        evaluation = self.evaluator.evaluations.get(deck_id)
        if not evaluation:
            return

        # 1. 対戦回数による信頼性（最大40点）
        # - 10試合未満: 試合数 * 4
        # - 10試合以上: 40点
        games_score = min(evaluation.games_played * 4, 40)

        # 2. レーティングの範囲（-60から+60点）
        # - 1000未満: -60点
        # - 1000-2000: 比例配分
        # - 2000以上: +60点
        rating = evaluation.rating
        if rating < 1000:
            rating_score = -60
        elif rating > 2000:
            rating_score = 60
        else:
            # 1000-2000の範囲を-60から+60にマッピング
            rating_score = (rating - 1500) / 500 * 60

        # 総合スコアの計算
        reference_score = games_score + rating_score

        # データベースを更新
        await asyncio.to_thread(
            update_deck_rating,
            deck_id,
            evaluation.rating,
            reference_score=reference_score,
        )

        logger.info(
            f"参考度合い更新 - Deck{deck_id}: {reference_score:.1f} "
            f"(試合数: {games_score:.1f}, レーティング: {rating_score:.1f})"
        )


# シングルトンインスタンス
simulation_manager = SimulationManager()
