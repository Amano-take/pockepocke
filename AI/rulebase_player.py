import logging
import pickle
import random
from typing import Callable, Dict

from game.deck import Deck
from game.energy import Energy
from game.game import Game
from game.player import Player
from game.exceptions import GameOverException

logger = logging.getLogger(__name__)


class RuleBasePlayer(Player):
    def __init__(self, deck: Deck, energy_candidates: list[Energy]):
        super().__init__(deck, energy_candidates)
        self.logger = logging.getLogger(__name__)

    def calculate_action_score(self) -> float:
        """
        Calculate the score for the current game state.
        Considers multiple factors including:
        - Active Pokemon HP and energy
        - Bench Pokemon status
        - Hand size
        - Side cards
        - Opponent's state
        """
        score = 0.0

        # Active Pokemon evaluation (35 points max)
        if self.active_pockemon:
            # HP evaluation (20 points max)
            score += self.active_pockemon.hp * 0.2
            # Energy evaluation (15 points max)
            total_energy = sum(self.active_pockemon.energies.energies)
            score += total_energy * 6

        # Opponent's Active Pokemon evaluation (-35 points max)
        if self.opponent.active_pockemon:
            score -= self.opponent.active_pockemon.hp * 0.2
            opp_total_energy = sum(self.opponent.active_pockemon.energies.energies)
            score -= opp_total_energy * 3

        # Bench evaluation (30 points max)
        bench_hp_total = sum(p.hp for p in self.bench)
        score += bench_hp_total * 0.1
        score += len(self.bench) * 6

        # Opponent's bench evaluation (-20 points max)
        score -= len(self.opponent.bench) * 4

        # Hand size evaluation (20 points max)
        total_hand = (
            len(self.hand_pockemon) + len(self.hand_goods) + len(self.hand_trainer)
        )
        score += total_hand * 2

        # Side cards evaluation (45 points max)
        score += self.sides * 30

        return score

    def prepare(self, phase: str = "select_active"):
        if phase == "select_active":
            self.pockemon_active_select()
            self.pockemon_bench_select()
        elif phase == "select_bench":
            self.pockemon_bench_select()
        else:
            raise ValueError(f"Invalid phase: {phase}")

    # 通常ターンの行動
    def start_turn(self, can_evolve: bool = True, phase: str = "goods"):
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

    def select_action(
        self, selection: Dict[int, str], action: Dict[int, Callable]
    ) -> int:
        """RuleBaseによる自動選択"""
        if len(selection) == 1:
            return 0

        if self.is_random:
            return random.randint(0, len(selection) - 1)

        ids = set()

        for card in self.deck.cards:
            ids.add(card.id_)

        # picklesave
        self.save_pkl()
        self.opponent.save_pkl()
        scores = {}
        for key in selection.keys():
            self.opponent.set_random()
            try:
                action[key]()
            except GameOverException as e:
                if e.winner.name == self.name:
                    scores[key] = float("inf")
                else:
                    scores[key] = -float("inf")
                continue
            scores[key] = self.calculate_action_score()
            self.load_pkl()
            self.opponent.load_pkl()

        for card in self.deck.cards:
            assert card.id_ in ids

        self.delete_pkl()
        self.opponent.delete_pkl()

        logger.debug(f"scores: {scores}")
        logger.debug(f"selection: {selection}")
        ans = max(scores, key=lambda k: scores[k])
        logger.debug(f"ans: {ans}")
        return ans
