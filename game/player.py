from __future__ import annotations
import game.utils
import logging
import random

from game.deck import Deck
from game.energy import Energy
from game.cards.pockemon_card import PockemonCard


logger = logging.getLogger(__name__)


class Player:
    def __init__(self, deck: Deck, energies: list[Energy]):
        self.deck = deck
        self.energy_candidates = energies
        self.hand_pockemon = []
        self.hand_goods = []
        self.hand_trainer = []
        self.bench = []
        self.active_pockemon = None
        self.sides = 0
        self.current_energy = None

    def __str__(self):
        return "プレイヤー" + str(random.randint(1, 100))

    def draw(self, number: int = 1):
        for _ in range(number):
            if len(self.deck.cards) == 0:
                logger.info("デッキが空です")
                return
            card = self.deck.draw()
            if isinstance(card, PockemonCard):
                self.hand_pockemon.append(card)
            else:
                # TODO: グッズとトレーナーの場合
                pass
        logger.debug(f"{self}が{number}枚引いた")
        logger.debug(f"手札ポケモン: {self.hand_pockemon}")
        logger.debug(f"手札グッズ: {self.hand_goods}")
        logger.debug(f"手札トレーナー: {self.hand_trainer}")

    def prepare(self):
        # active_pockemonを選ぶ
        selection = {}
        candidates = {}
        manage_duplicates = set()
        for i, card in enumerate(self.hand_pockemon):
            assert isinstance(card, PockemonCard)
            if card.is_seed:
                if card.name in manage_duplicates:
                    continue
                manage_duplicates.add(card.name)
                selection[len(selection)] = f"{card.name}をバトル場に出す"
                candidates[len(candidates)] = i
        i = self.select_action(selection)
        self.active_pockemon = self.hand_pockemon.pop(candidates[i])

    def attach_energy(self, card: PockemonCard):
        card.energies.attach_energy(self.current_energy)
        logger.debug(f"{self}が{self.current_energy}を{card}につけた")
        self.current_energy = None

    def get_energy(self):
        i = random.randint(0, len(self.energy_candidates) - 1)
        logger.debug(f"{self}が{self.energy_candidates[i]}を手に入れた")
        self.current_energy = self.energy_candidates[i]

    # 選択肢を受け取り行動を選択する。今のところはinput()で選択することに、ここをAI化するのが目標
    def select_action(self, selection: dict[int, str]):
        if len(selection) == 1:
            return 0
        logger.info("選択してください")
        for key, value in selection.items():
            logger.info(f"{key}: {value}")
        i = int(input())
        assert i in selection
        return i


if __name__ == "__main__":
    from game.deck import Deck
    from game.energy import Energy
    from game.cards.pockemon_card import PockemonCard
