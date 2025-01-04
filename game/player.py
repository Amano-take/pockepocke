from __future__ import annotations
import game.utils
import logging
import random
from itertools import combinations

from game.deck import Deck
from game.energy import Energy
from game.cards.pockemon_card import PockemonCard
from game.cards.goods_cards.goods import GoodsCard


logger = logging.getLogger(__name__)


class Player:
    def __init__(self, deck: Deck, energies: list[Energy]):
        self.name = "プレイヤー" + str(random.randint(1, 100))
        self.deck = deck
        self.energy_candidates = energies
        self.energy_values = [1] * len(Energy)
        self.hand_pockemon: list[PockemonCard] = []
        self.hand_goods: list[GoodsCard] = []
        self.hand_trainer = []
        self.bench: list[PockemonCard] = []
        self.active_pockemon = None
        self.sides = 0
        self.current_energy = None
        # ターンを終わったときの処理
        self.processes_at_end_of_turn = []

    def __str__(self):
        return self.name

    def set_game(self, game: Game):
        self.game = game

    def draw(self, number: int = 1):
        for _ in range(number):
            if len(self.deck.cards) == 0:
                logger.info("デッキが空です")
                return
            card = self.deck.draw()
            if isinstance(card, PockemonCard):
                self.hand_pockemon.append(card)
            elif isinstance(card, GoodsCard):
                self.hand_goods.append(card)
            else:
                # TODO: トレーナーの場合
                pass
        logger.debug(f"{self}が{number}枚引いた")
        logger.debug(f"手札ポケモン: {self.hand_pockemon}")
        logger.debug(f"手札グッズ: {self.hand_goods}")
        logger.debug(f"手札トレーナー: {self.hand_trainer}")

    # 準備ターンの行動
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

        selection_list = []
        for i, card in enumerate(self.hand_pockemon):
            assert isinstance(card, PockemonCard)
            if card.is_seed:
                selection_list.append(i)

        selection = {}
        candidates = {}
        manage_duplicates = set()
        for i in range(0, min(3, len(selection_list)) + 1):
            for comb in combinations(selection_list, i):
                if tuple(sorted([self.hand_pockemon[j].name for j in comb])) in manage_duplicates:
                    continue
                manage_duplicates.add(tuple(sorted([self.hand_pockemon[j].name for j in comb])))
                selection[len(selection)] = f"{[self.hand_pockemon[j].name for j in comb]}をベンチに出す"
                candidates[len(candidates)] = comb

        i = self.select_action(selection)
        for j in candidates[i]:
            self.bench.append(self.hand_pockemon[j])

        # comb番目を手札から削除
        for j in sorted(candidates[i], reverse=True):
            self.hand_pockemon.pop(j)

        logger.debug(f"{self}が{self.active_pockemon}をアクティブに出した")
        logger.debug(f"{self}が{self.bench}をベンチに出した")
        logger.debug(f"手札ポケモン: {self.hand_pockemon}")

    # 通常ターンの行動
    def start_turn(self, can_attack: bool = True, can_evolve: bool = True):
        # TODO: 行動順の仮定を行う必要がある
        # goodsを使う
        self.use_goods()
        # trainerを使う
        self.use_trainer()
        # 手札のポケモンを出す
        # 手札のポケモンを進化させる
        # エネルギーをつける
        # 逃げる
        # 攻撃する or ターン終了
        pass

    # エネルギーをつける
    def attach_energy(self, card: PockemonCard):
        card.attach_energy(self.current_energy)
        logger.debug(f"{self}が{self.current_energy}を{card}につけた")
        self.current_energy = None

    def get_energy(self):
        i = random.randint(0, len(self.energy_candidates) - 1)
        logger.debug(f"{self}が{self.energy_candidates[i]}を手に入れた")
        self.current_energy = self.energy_candidates[i]

    def use_goods(self):
        goods_cards: list[GoodsCard] = []
        for card in self.hand_goods[:]:
            if card.name == "MonsterBall":
                card.use(self.game)
                logger.debug(f"{self}が{card}を使った")
                logger.debug(f"手札ポケモン: {self.hand_pockemon}")
            else:
                goods_cards.append(card)

        # それぞれ使うか使わないか,2**len(goods_cards)通り
        selection = {}
        candidates: dict[int, list[GoodsCard]] = {}
        manage_duplicates = set()
        for i in range(2 ** len(goods_cards)):
            use_goods: list[GoodsCard] = []
            for j, card in enumerate(goods_cards):
                if (i >> j) & 1:
                    use_goods.append(card)
            if tuple(sorted([card.name for card in use_goods])) in manage_duplicates:
                continue
            manage_duplicates.add(tuple(sorted([card.name for card in use_goods])))
            selection[len(selection)] = f"{[card.name for card in use_goods]}を使う"
            candidates[len(candidates)] = use_goods

        i = self.select_action(selection)
        for card in candidates[i]:
            card.use(self.game)

    def use_trainer(self):
        pass

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
    from game.game import Game
