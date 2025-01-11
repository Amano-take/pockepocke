from __future__ import annotations

import logging
import random
from itertools import combinations, chain, product
from collections import defaultdict as ddict

from game.exceptions import GameOverException
import game.utils

from game.deck import Deck
from game.energy import Energy
from game.cards.pockemon_card import PockemonCard
from game.cards.goods_cards.goods import GoodsCard
from game.cards.trainer_cards.trainers import TrainerCard
from game.cards.pockemon_card import PockemonAttack


logger = logging.getLogger(__name__)


class Player:
    def __init__(self, deck: Deck, energies: list[Energy]):
        self.name = "player" + str(random.randint(1, 100))
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
        self.trash = []
        # ターンを終わったときの処理
        self.processes_at_end_of_turn = []
        # ターンを始めたときの処理

    def set_game(self, game: Game):
        self.game = game
        if game.player1 is self:
            self.opponent = game.player2
        else:
            self.opponent = game.player1
        self.deck.set_player(self)

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
                self.hand_trainer.append(card)
                pass
        logger.debug(f"{self}が{number}枚引いた")

    def prepare_active_pockemon(self, card: PockemonCard):
        self.active_pockemon = card
        card.enter_battle()
        self.hand_pockemon.remove(card)

    def prepare_bench_pockemon(self, card: PockemonCard):
        self.bench.append(card)
        card.enter_battle()
        self.hand_pockemon.remove(card)

    def prepare_active_pockemon_from_bench(self, card: PockemonCard):
        assert card in self.bench
        self.bench.remove(card)
        self.active_pockemon = card

    def candidate_attack(self):
        return self.active_pockemon.candidate_attacks()

    def attack(self, attack: None | PockemonAttack):
        if attack is None:
            return
        attack.attack(self.game)

    # 準備ターンの行動
    def prepare(self):
        # active_pockemonを選ぶ
        selection = {}
        action = {}
        manage_duplicates = set()
        for i, card in enumerate(self.hand_pockemon):
            assert isinstance(card, PockemonCard)
            if card.is_seed:
                if card.name in manage_duplicates:
                    continue
                manage_duplicates.add(card.name)
                selection[len(selection)] = f"{card.name}をバトル場に出す"
                action[len(action)] = lambda card=card: self.prepare_active_pockemon(
                    card
                )
        i = self.select_action(selection, action)
        action[i]()

        # benchを選ぶ
        selection_list = []
        for i, card in enumerate(self.hand_pockemon):
            assert isinstance(card, PockemonCard)
            if card.is_seed:
                selection_list.append(i)

        selection = {}
        action = {}
        manage_duplicates = set()
        for i in range(0, min(3, len(selection_list)) + 1):
            for comb in combinations(selection_list, i):
                if (
                    tuple(sorted([self.hand_pockemon[j].name for j in comb]))
                    in manage_duplicates
                ):
                    continue
                manage_duplicates.add(
                    tuple(sorted([self.hand_pockemon[j].name for j in comb]))
                )
                selection[len(selection)] = (
                    f"{[self.hand_pockemon[j].name for j in comb]}をベンチに出す"
                )
                action[len(action)] = lambda comb=comb: [
                    self.prepare_bench_pockemon(self.hand_pockemon[j]) for j in comb
                ]

        i = self.select_action(selection, action)
        action[i]()

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
        # 手札のポケモンを進化させる
        self.evolve_select()
        # 手札のポケモンを出す
        self.use_pockemon_select()
        # エネルギーをつける
        self.attach_energy_select()
        # 特性を使う
        self.use_feature_select()
        # 逃げる
        self.retreat_select()
        # 攻撃する or ターン終了
        self.attack_select()
        return

    def attack_select(self):
        attack_list = self.candidate_attack()
        selection = {}
        action = {}
        selection[len(selection)] = "ターンを終了する"
        action[len(action)] = lambda: None
        for i, attack in enumerate(attack_list):
            selection[len(selection)] = f"{attack}を使う"
            action[len(action)] = lambda attack=attack: self.attack(attack)

        i = self.select_action(selection, action)
        action[i]()

    def use_feature_select(self):
        for card in [self.active_pockemon] + self.bench:
            card.feature_active()

        return

    def retreat(self, card: PockemonCard):
        assert card in self.bench
        self.bench[self.bench.index(card)], self.active_pockemon = (
            self.active_pockemon,
            card,
        )
        logger.debug(f"{self}が{card}をアクティブに出した")

    def retreat_select(self):
        selection = {}
        action = {}
        selection[len(selection)] = "逃げない"
        action[len(action)] = lambda: None
        for i, card in enumerate(self.bench):
            selection[len(selection)] = f"{card}をアクティブに出す"
            action[len(action)] = lambda card=card: self.retreat(card)

        i = self.select_action(selection, action)
        action[i]()

    def evolve_select(self):
        # 進化するポケモンを選ぶ
        field_pockemon = ddict(list)
        for i, card in enumerate([self.active_pockemon] + self.bench):
            field_pockemon[card.name].append(card)

        selection = []
        for name, cards in field_pockemon.items():
            # 手札の進化先ポケモンを探す
            count = 0
            for hand in self.hand_pockemon:
                hand: PockemonCard
                if hand.previous_pockemon == name:
                    count += 1
            if count == 0:
                continue

            evolve_list = []
            for i in range(min(count, len(cards)) + 1):
                for comb in combinations(cards, i):
                    evolve_list.append(comb)

            selection.append(evolve_list)

        # selectionの各要素の直積を取る
        result = [tuple(chain(*prod)) for prod in product(*selection)]
        selection = {}
        action = {}
        for act in result:
            selection[len(selection)] = f"{[card.name for card in act]}を進化させる"
            action[len(action)] = [lambda card=card: self.evolve(card) for card in act]

        i = self.select_action(selection, action)
        for act in action[i]:
            act()

    def evolve(self, card: PockemonCard):
        if not (card is self.active_pockemon or card in self.bench):
            return False

        for hand in self.hand_pockemon:
            if hand.previous_pockemon == card.name:
                # 受けているダメージは引き継ぐ
                damage = card.max_hp - card.hp
                if card is self.active_pockemon:
                    self.active_pockemon = hand
                    hand.hp = hand.max_hp - damage
                    logger.debug(f"{self}がactiveな{card.name}を{hand}へ進化させた")
                else:
                    self.bench[self.bench.index(card)] = hand
                    hand.hp = hand.max_hp - damage
                    logger.debug(f"{self}がbenchの{card.name}を{hand}へ進化させた")
                self.hand_pockemon.remove(hand)
                return True

        return False

    # エネルギーをつける
    def attach_energy(self, card: PockemonCard):
        card.attach_energy(self.current_energy)
        logger.debug(f"{self}が{self.current_energy}を{card}につけた")
        self.current_energy = None

    def attach_energy_select(self):
        """現在のエネルギーをどのポケモンにつけるか選択する, つけない場合もある"""
        if not self.current_energy:
            return

        selection = {}
        action = {}

        # つけない場合
        selection[len(selection)] = "エネルギーをつけない"
        action[len(action)] = lambda: None

        # アクティブポケモン
        if self.active_pockemon:
            selection[len(selection)] = f"{self.active_pockemon}にエネルギーをつける"
            action[len(action)] = lambda: self.attach_energy(self.active_pockemon)

        # ベンチポケモン
        for i, card in enumerate(self.bench):
            selection[len(selection)] = f"{card}にエネルギーをつける"
            action[len(action)] = lambda card=card: self.attach_energy(card)

        i = self.select_action(selection, action)
        action[i]()

    def get_energy(self):
        i = random.randint(0, len(self.energy_candidates) - 1)
        logger.debug(f"{self}が{self.energy_candidates[i]}を手に入れた")
        self.current_energy = self.energy_candidates[i]

    def attack_buff(self, value: int):
        self.attack_buff = value

    def retreat_buff(self, value: int):
        self.retreat_buff = value

    def use_goods(self):
        goods_cards: list[GoodsCard] = []
        for card in self.hand_goods[:]:
            if card.name == "MonsterBall":
                card.use(self.game)
                logger.debug(f"{self}が{card}を使った")
            elif card.can_use(self.game):
                goods_cards.append(card)

        # それぞれ使うか使わないか,2**len(goods_cards)通り
        selection = {}
        action = {}
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
            action[len(action)] = lambda use_goods=use_goods: [
                card.use(self.game) for card in use_goods
            ]

        i = self.select_action(selection, action)
        action[i]()
        logger.debug(f"{self}が{selection[i]}を使った")

    def use_trainer(self):
        trainer_cards: list[TrainerCard] = []
        for card in self.hand_trainer[:]:
            if card.can_use(self.game):
                trainer_cards.append(card)

        # 使用するかどうかの選択肢
        selection = {}
        action = {}
        manage_duplicates = set()

        # 使用しない選択肢を追加
        selection[len(selection)] = "トレーナーカードを使用しない"
        action[len(action)] = lambda: None

        # 各トレーナーカード単体での使用
        for card in trainer_cards:
            if card.name in manage_duplicates:
                continue
            manage_duplicates.add(card.name)
            selection[len(selection)] = f"{card.name}を使う"
            action[len(action)] = lambda card=card: card.use(self.game)

        i = self.select_action(selection, action)
        action[i]()

    def use_pockemon_select(self):
        # benchを選ぶ
        selection_list = []
        for i, card in enumerate(self.hand_pockemon):
            assert isinstance(card, PockemonCard)
            if card.is_seed:
                selection_list.append(i)

        selection = {}
        action = {}
        manage_duplicates = set()
        for i in range(0, min(3 - len(self.bench), len(selection_list)) + 1):
            for comb in combinations(selection_list, i):
                if (
                    tuple(sorted([self.hand_pockemon[j].name for j in comb]))
                    in manage_duplicates
                ):
                    continue
                manage_duplicates.add(
                    tuple(sorted([self.hand_pockemon[j].name for j in comb]))
                )
                selection[len(selection)] = (
                    f"{[self.hand_pockemon[j].name for j in comb]}をベンチに出す"
                )
                action[len(action)] = lambda comb=comb: [
                    self.prepare_bench_pockemon(self.hand_pockemon[j]) for j in comb
                ]

        i = self.select_action(selection, action)
        action[i]()

        logger.debug(f"{self}が{self.active_pockemon}をアクティブに出した")

    def select_bench(self):
        # active_pockemonが倒されたときの処理
        if len(self.bench) == 0:
            raise GameOverException("勝利プレイヤー: " + str(self.opponent))

        selection = {}
        action = {}
        for i, card in enumerate(self.bench):
            selection[len(selection)] = f"{card}をアクティブに出す"
            action[len(action)] = (
                lambda card=card: self.prepare_active_pockemon_from_bench(card)
            )

        choice = self.select_action(selection, action)
        action[choice]()

        logger.debug(f"{self}が{self.active_pockemon}をアクティブに出した")

    # 選択肢を受け取り行動を選択する。今のところはinput()で選択することに、ここをAI化するのが目標
    def select_action(
        self, selection: dict[int, str], action: dict[int, callable] = {}
    ):
        if len(selection) == 1:
            return 0
        logger.info("選択してください")
        for key, value in selection.items():
            logger.info(f"{key}: {value}")
        i = int(input())
        assert i in selection
        return i

    def __str__(self):
        return self.name


if __name__ == "__main__":
    from game.game import Game
