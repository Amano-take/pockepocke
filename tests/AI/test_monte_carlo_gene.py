import unittest
import random
import logging
from pathlib import Path

from game.game import Game
from game.deck import Deck
from game.energy import Energy
from game.exceptions import GameOverException
from AI.monte_carlo_gene import MonteCarloGenePlayer
from tests.utils.set_lightning import lightning_deck

# テスト用にログレベルを設定
logging.basicConfig(level=logging.INFO)

class TestMonteCarloGenePlayer(unittest.TestCase):
    def setUp(self):
        # エネルギーリストの準備
        self.energies = [Energy.LIGHTNING]  # lightning_deckに合わせて変更
        self.deck_list = lightning_deck()

    def _test_game_completion(self):
        """モンテカルロプレイヤー同士の対戦が正常に終了するかテスト"""
        # プレイヤーの準備
        deck1 = Deck(self.deck_list)
        deck2 = Deck(self.deck_list)
        player1 = MonteCarloGenePlayer(deck1, self.energies)
        player2 = MonteCarloGenePlayer(deck2, self.energies)

        # 乱数シードを固定（再現性のため）
        random.seed(42)

        # ゲームの初期化
        game = Game()
        game.set_players(player1, player2)

        try:
            # ゲームを実行
            game.start()
            self.fail("GameOverExceptionが発生しませんでした")
        except GameOverException as e:
            # 正常にゲームが終了したことを確認
            self.assertIsNotNone(e.winner)
            self.assertIn(e.winner, [player1, player2])
            logging.info(f"Winner: {e.winner.name}")

    def _test_single_turn_execution(self):
        """1ターンの実行が正常に行われるかテスト"""
        # プレイヤーの準備
        deck1 = Deck(self.deck_list)
        deck2 = Deck(self.deck_list)
        player1 = MonteCarloGenePlayer(deck1, self.energies)
        player2 = MonteCarloGenePlayer(deck2, self.energies)

        # ゲームの初期化
        game = Game()
        game.set_players(player1, player2)

        # 準備フェーズ
        player1.prepare()
        player2.prepare()

        # 1ターン実行
        try:
            player1.start_turn()
            logging.info("Player 1 completed their turn successfully")
        except Exception as e:
            self.fail(f"ターンの実行中にエラーが発生: {str(e)}")

if __name__ == '__main__':
    unittest.main()
