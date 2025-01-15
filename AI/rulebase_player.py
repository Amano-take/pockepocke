from game.player import Player
from game.game import Game
import logging
import pickle
from typing import Dict, Callable

logger = logging.getLogger(__name__)


class RuleBasePlayer(Player):
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
            score += total_energy * 3

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

    def load_pkl(self):
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

    def select_action(
        self, selection: Dict[int, str], action: Dict[int, Callable] = {}
    ) -> int:
        """RuleBaseによる自動選択"""
        if len(selection) == 1:
            return 0

        # picklesave
        with open("./player.pkl", "wb") as f:
            pickle.dump(self, f)

        scores = {}
        for key in selection.keys():
            # TODO: 相手の行動が必要なactionの場合バグの発生
            action[key]()
            scores[key] = self.calculate_action_score()
            self.load_pkl()

        logger.debug(f"scores: {scores}")
        logger.debug(f"selection: {selection}")
        ans = max(scores, key=scores.get)
        logger.debug(f"ans: {ans}")
        return ans
