from game.player import Player
import logging
import pickle
from typing import Dict, Callable

logger = logging.getLogger(__name__)


class RuleBasePlayer(Player):
    def calculate_action_score(self) -> float:
        """行動のスコアを計算する"""
        score = 0.0

        # アクティブポケモンのHP (30)
        if self.active_pockemon:
            score += self.active_pockemon.hp * 0.3

        # 相手のアクティブポケモンのHP (30)
        if self.opponent.active_pockemon:
            score -= self.opponent.active_pockemon.hp * 0.3

        # サイドの状況 ( 45 )
        score += self.sides * 30

        # ベンチポケモンの数 ( 10 )
        score += len(self.bench) * 10

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

        id_ = id(self)
        hash_ = hash(self)

        scores = {}
        for key in selection.keys():
            action[key]()
            scores[key] = self.calculate_action_score()
            self.load_pkl()

        assert id(self) == id_
        assert hash(self) == hash_

        logger.debug(f"scores: {scores}")
        # max index
        return max(scores, key=scores.get)
