from dataclasses import dataclass
from typing import List, Dict, Optional
import asyncio
import logging
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.append(str(Path(__file__).resolve().parents[1]))

from game.game import Game
from game.deck import Deck
from game.player import Player
from AI.rulebase_player import RuleBasePlayer
from server.database import (
    update_deck_rating,
    get_all_client_ids,
    get_decks_by_client_id,
)
from ratings.rating_system import EloRating
from game.cards import ALL_CARDS
from game.energy import Energy

logger = logging.getLogger(__name__)


@dataclass
class DeckEvaluation:
    """デッキの評価結果"""

    deck_id: int
    rating: float
    games_played: int
    wins: int
    confidence_score: float


class DeckEvaluator:
    """デッキの評価を行うクラス"""

    def __init__(self):
        self.rating_system = EloRating()
        self.evaluations: Dict[int, DeckEvaluation] = {}
        self.executor = ThreadPoolExecutor(
            max_workers=4
        )  # 同時に実行できるゲーム数を制限

    def _convert_card_names_to_objects(self, card_names: List[str]) -> list:
        """カード名からカードオブジェクトのリストを生成"""
        cards = []
        for name in card_names:
            for card_class in ALL_CARDS:
                if card_class.__name__ == name:
                    cards.append(card_class())
                    break
        return cards

    def _run_game_in_thread(
        self,
        deck1_cards: List[str],
        deck2_cards: List[str],
        deck1_energy: str,
        deck2_energy: str,
    ) -> bool:
        """スレッド内でゲームを実行"""
        try:
            # カードオブジェクトに変換
            cards1 = self._convert_card_names_to_objects(deck1_cards)
            cards2 = self._convert_card_names_to_objects(deck2_cards)

            # デッキが空の場合は評価をスキップ
            if not cards1 or not cards2:
                logger.warning("Empty deck detected, skipping evaluation")
                return False

            # エナジータイプをEnergy型に変換
            energy_mapping = {
                "grass": Energy.GRASS,
                "fire": Energy.FIRE,
                "water": Energy.WATER,
                "lightning": Energy.LIGHTNING,
                "psychic": Energy.PSYCHIC,
                "fighting": Energy.FIGHTING,
            }
            energy1 = [energy_mapping.get(deck1_energy, Energy.GRASS)]
            energy2 = [energy_mapping.get(deck2_energy, Energy.GRASS)]

            # デッキを作成
            deck1 = Deck(cards1)
            deck2 = Deck(cards2)

            # プレイヤーを作成（両方ルールベースAI）
            player1 = RuleBasePlayer(deck1, energy1)
            player2 = RuleBasePlayer(deck2, energy2)

            # ゲームを作成
            game = Game()
            game.set_players(player1, player2)

            # すべてのロガーのレベルを WARNING に設定
            game.set_level(logging.WARNING)
            player1.set_logger(logging.WARNING)
            player2.set_logger(logging.WARNING)

            # ゲームを実行（start()で最後まで実行される）
            game.start()

            # 勝者を判定（ゲーム終了後はwinnerが設定されている）
            return game.winner == player1

        except Exception as e:
            logger.error(f"Error during game simulation: {e}")
            return False  # エラーが発生した場合は負けとする

    async def evaluate_deck(
        self,
        deck_id: int,
        deck_cards: List[str],
        opponent_decks: List[tuple[int, List[str]]],
    ) -> DeckEvaluation:
        """デッキを評価する"""
        if deck_id not in self.evaluations:
            self.evaluations[deck_id] = DeckEvaluation(
                deck_id=deck_id,
                rating=self.rating_system.initial_rating,
                games_played=0,
                wins=0,
                confidence_score=0.0,
            )

        evaluation = self.evaluations[deck_id]

        # 各対戦相手と対戦
        for opponent_id, opponent_cards in opponent_decks:
            if opponent_id == deck_id:
                continue

            # 対戦をスレッドプールで実行
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._run_game_in_thread,
                deck_cards,
                opponent_cards,
                "grass",
                "grass",
            )

            # 対戦結果に基づいてレーティングを更新
            opponent_rating = self.evaluations.get(
                opponent_id,
                DeckEvaluation(
                    deck_id=opponent_id,
                    rating=self.rating_system.initial_rating,
                    games_played=0,
                    wins=0,
                    confidence_score=0.0,
                ),
            ).rating

            new_rating, new_opponent_rating = self.rating_system.calculate_new_ratings(
                evaluation.rating, opponent_rating, 1.0 if result else 0.0
            )

            # 評価情報を更新
            evaluation.rating = new_rating
            evaluation.games_played += 1
            if result:
                evaluation.wins += 1
            evaluation.confidence_score = self.rating_system.get_confidence_level(
                evaluation.games_played
            )

            # データベースを更新
            await asyncio.to_thread(
                update_deck_rating,
                deck_id,
                new_rating,
                result,
                games_played=evaluation.games_played,
                wins=evaluation.wins,
            )

            # 対戦相手の評価も更新
            if opponent_id in self.evaluations:
                self.evaluations[opponent_id].rating = new_opponent_rating
                await asyncio.to_thread(
                    update_deck_rating,
                    opponent_id,
                    new_opponent_rating,
                    not result,
                    games_played=self.evaluations[opponent_id].games_played,
                    wins=self.evaluations[opponent_id].wins,
                )

        return evaluation

    async def evaluate_match(
        self,
        deck1_id: int,
        deck1_cards: List[str],
        deck1_energy: str,
        deck2_id: int,
        deck2_cards: List[str],
        deck2_energy: str,
    ) -> bool:
        """2つのデッキ間の対戦を評価する

        Args:
            deck1_id: デッキ1のID
            deck1_cards: デッキ1のカードリスト
            deck1_energy: デッキ1のエナジータイプ
            deck2_id: デッキ2のID
            deck2_cards: デッキ2のカードリスト
            deck2_energy: デッキ2のエナジータイプ

        Returns:
            デッキ1が勝利した場合True
        """
        # 対戦をスレッドプールで実行
        result = await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self._run_game_in_thread,
            deck1_cards,
            deck2_cards,
            deck1_energy,
            deck2_energy,
        )

        # データベースから最新の情報を取得
        client_ids = await asyncio.to_thread(get_all_client_ids)
        deck1_data = None
        deck2_data = None

        for client_id in client_ids:
            decks = await asyncio.to_thread(get_decks_by_client_id, client_id)
            for deck in decks:
                if deck["id"] == deck1_id:
                    deck1_data = deck
                if deck["id"] == deck2_id:
                    deck2_data = deck
            if deck1_data and deck2_data:
                break

        if deck1_data and deck2_data:
            # レーティングを計算
            new_rating1, new_rating2 = self.rating_system.calculate_new_ratings(
                float(deck1_data["rating"]),
                float(deck2_data["rating"]),
                1.0 if result else 0.0,
            )

            # データベースを更新
            await asyncio.to_thread(
                update_deck_rating,
                deck1_id,
                new_rating1,
                won=result,
            )
            await asyncio.to_thread(
                update_deck_rating,
                deck2_id,
                new_rating2,
                won=not result,
            )

        return result
