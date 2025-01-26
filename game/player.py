from __future__ import annotations

import logging
import os
import pickle
import random
from collections import defaultdict as ddict
from itertools import chain, combinations, product
from typing import Callable

import game.utils
from game.cards.goods_cards.goods import GoodsCard
from game.cards.pockemon_card import PockemonAttack, PockemonCard
from game.cards.trainer_cards.trainers import TrainerCard
from game.deck import Deck
from game.energy import Energy
from game.exceptions import GameOverException

logger = logging.getLogger(__name__)


class Player:
    def __init__(self, deck: Deck, energies: list[Energy]):
        self.name = "player" + str(random.randint(1, 100))
        self.deck = deck
        self.energy_candidates = energies
        self.energy_values = [1] * len(Energy)
        self.is_random = False  # Flag for random action selection
        self.hand_pockemon: list[PockemonCard] = []
        self.hand_goods: list[GoodsCard] = []
        self.hand_trainer: list[TrainerCard] = []
        self.bench: list[PockemonCard] = []
        self.sides = 0
        self.current_energy = None
        self.trash = []
        # temp variable
        self.active_pockemon: PockemonCard = PockemonCard()
        # ターンを終わったときの処理
        self.processes_at_end_of_turn = []
        self.init_buff()

    def init_buff(self):
        self.attack_buff_value = 0
        self.retreat_cost_buff = 0

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
                logger.info(f"【{self.name}】デッキが空になりました")
                return
            card = self.deck.draw()
            if isinstance(card, PockemonCard):
                self.hand_pockemon.append(card)
            elif isinstance(card, GoodsCard):
                self.hand_goods.append(card)
            elif isinstance(card, TrainerCard):
                self.hand_trainer.append(card)
                pass
        logger.debug(f"【{self.name}】カードを{number}枚ドローしました")

    def prepare_active_pockemon(self, card: PockemonCard):
        self.active_pockemon: PockemonCard = card
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
        assert self.active_pockemon
        return self.active_pockemon.candidate_attacks()

    def attack(self, attack: None | PockemonAttack, target: PockemonCard | None = None):
        if attack is None:
            return
        if target is None:
            target = self.opponent.active_pockemon
        if target != self.opponent.active_pockemon:
            attack.attack(self.game, target)
        else:
            attack.attack(self.game)

    # 準備ターンの行動
    def prepare(self):
        # active_pockemonを選ぶ
        self.pockemon_active_select()
        # benchを選ぶ
        self.pockemon_bench_select()

        logger.info(
            f"【{self.name}】{self.active_pockemon.name}をバトル場に配置しました"
        )
        if self.bench:
            logger.info(
                f"【{self.name}】ベンチに{', '.join([p.name for p in self.bench])}を配置しました"
            )
        logger.debug(
            f"【{self.name}】手札のポケモン: {[p.name for p in self.hand_pockemon]}"
        )

    def pockemon_active_select(self):
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

    def pockemon_bench_select(self):
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
                    self.prepare_bench_pockemon(self.hand_pockemon[j])
                    for j in reversed(comb)
                ]

        i = self.select_action(selection, action)
        action[i]()

    # 通常ターンの行動
    def start_turn(self, can_evolve: bool = True):
        # TODO: 行動順の仮定を行う必要がある
        # goodsを使う
        self.use_goods_select()
        # trainerを使う
        self.use_trainer_select()
        # 手札のポケモンを進化させる
        self.evolve_select(can_evolve)
        # 手札のポケモンを出す
        self.use_pockemon_select()
        # エネルギーをつける
        self.attach_energy_select()
        # 特性を使う　# TODO: 対象指定が必要な特性
        self.use_feature_select()
        # 逃げる
        self.retreat_select()
        # 攻撃する or ターン終了
        self.attack_select()
        self.end_turn()
        return

    def end_turn(self):
        self.attack_buff_value = 0
        self.retreat_cost_buff = 0

    def attack_select(self):
        attack_list = self.candidate_attack()
        selection = {}
        action = {}
        selection[len(selection)] = "ターンを終了する"
        action[len(action)] = lambda: None
        for i, attack in enumerate(attack_list):
            for target in attack.target_list(self.game):
                selection[len(selection)] = f"{attack}を{target.name}使う"
                action[len(action)] = lambda attack=attack, target=target: self.attack(
                    attack, target
                )

        i = self.select_action(selection, action)
        action[i]()

    def use_feature_select(self):
        for card in [self.active_pockemon] + self.bench:
            card.feature_active()

        return

    def retreat(self, card: PockemonCard, energies: list[Energy]):
        assert (
            (card in self.bench)
            and isinstance(card, PockemonCard)
            and isinstance(self.active_pockemon, PockemonCard)
        )
        self.active_pockemon.retreat(self.retreat_cost_buff, energies)
        self.bench[self.bench.index(card)], self.active_pockemon = (
            self.active_pockemon,
            card,
        )
        logger.info(f"【{self.name}】{card.name}をバトル場に移動しました")

    def retreat_select(self):
        selection = {}
        action = {}
        selection[len(selection)] = "逃げない"
        action[len(action)] = lambda: None
        manage_duplicates = set()
        if self.active_pockemon is None or not self.active_pockemon.can_retreat(
            self.retreat_cost_buff
        ):
            return
        for i, card in enumerate(self.bench):
            # active_pockemon.energyからretreat_cost - retreat_cost_buffを引いたものの場合の数を選択肢にする
            num: int = self.active_pockemon.retreat_cost - self.retreat_cost_buff
            for comb in combinations(self.active_pockemon.energies.flatten(), num):
                if (
                    sorted_name := (
                        card.id_,
                        "".join([energy.name for energy in comb]),
                    )
                ) in manage_duplicates:
                    continue
                manage_duplicates.add(sorted_name)
                selection[len(selection)] = (
                    f"{self.active_pockemon.name}は{card.name}と{[energy.name for energy in comb]}交代する。"
                )
                action[len(action)] = lambda card=card, comb=comb: self.retreat(
                    card, list(comb)
                )

        i = self.select_action(selection, action)
        action[i]()

    def evolve_select(self, can_evolve: bool = True):
        if not can_evolve:
            return

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

            def evolve(act=act):
                for card in act:
                    self.evolve(card)

            action[len(action)] = evolve

        i = self.select_action(selection, action)
        action[i]()

    def evolve(self, card: PockemonCard):
        if not (card == self.active_pockemon or card in self.bench):
            return False

        for hand in self.hand_pockemon:
            if hand.previous_pockemon == card.name:
                # 受けているダメージは引き継ぐ
                damage = card.max_hp - card.hp
                if card == self.active_pockemon:
                    self.active_pockemon = hand
                    hand.hp = hand.max_hp - damage
                    # energyも引き継ぐ
                    hand.energies = card.energies
                    logger.info(
                        f"【{self.name}】バトル場の{card.name}を{hand.name}に進化させました"
                    )
                else:
                    self.bench[self.bench.index(card)] = hand
                    hand.hp = hand.max_hp - damage
                    # energyも引き継ぐ
                    hand.energies = card.energies
                    logger.info(
                        f"【{self.name}】ベンチの{card.name}を{hand.name}に進化させました"
                    )
                self.hand_pockemon.remove(hand)
                return True

        return False

    # エネルギーをつける
    def attach_energy(self, card: PockemonCard):
        assert self.current_energy
        card.attach_energy(self.current_energy)
        logger.info(
            f"【{self.name}】{card.name}に{self.current_energy.name}エネルギーを付与しました"
        )
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
        logger.debug(
            f"【{self.name}】{self.energy_candidates[i].name}エネルギーを手に入れました"
        )
        self.current_energy = self.energy_candidates[i]

    def attack_buff(self, value: int):
        self.attack_buff_value = value

    def retreat_buff(self, value: int):
        self.retreat_cost_buff = value

    def use_goods_select(self):
        # ex. [[(kizugusuri, active), (kizugusuri, bench1)], (redcard), ...]
        goods_cards: list[list[tuple[GoodsCard, PockemonCard]] | GoodsCard] = []
        for card in self.hand_goods:
            if card.name == "MonsterBall":
                card.use(self.game)
                logger.info(f"【{self.name}】{card.name}を使用しました")
            elif use_list := card.can_use(self.game):
                # 対象なし
                if use_list is True:
                    goods_cards.append(card)
                # 対象あり
                elif isinstance(use_list, list):
                    goods_cards.append([(card, pockemon) for pockemon in use_list])

        # それぞれ使うか使わないか,2**len(goods_cards)通り * 対象の選択肢
        selection = {}
        action = {}
        selection[len(selection)] = "グッズカードを使用しない"
        action[len(action)] = lambda: None
        manage_duplicates = set()
        for i in range(1, 2 ** len(goods_cards)):
            use_goods_list: list[list[tuple[GoodsCard, PockemonCard | None]]] = [[]]
            for j, card in enumerate(goods_cards):
                card: GoodsCard | list[tuple[GoodsCard, PockemonCard]]
                if (i >> j) & 1:
                    if isinstance(card, GoodsCard):
                        for use_goods in use_goods_list:
                            use_goods.append((card, None))
                    else:
                        temp_list = []
                        for goods, pockemon in card:
                            for use_goods in use_goods_list:
                                use_goods = use_goods[:]
                                use_goods.append((goods, pockemon))
                                temp_list.append(use_goods)
                        use_goods_list = temp_list

            for use_goods in use_goods_list:
                if (
                    sorted_name := tuple(
                        sorted(
                            [(card.name, id(pockemon)) for card, pockemon in use_goods]
                        )
                    )
                ) in manage_duplicates:
                    continue
                manage_duplicates.add(sorted_name)
                selection[len(selection)] = (
                    f"{[(card.name + 'を' + pockemon.name + 'に' if isinstance(pockemon, PockemonCard) else card.name) for card, pockemon in use_goods]}"
                )
                action[len(action)] = lambda use_goods=use_goods: [
                    (
                        card.use(self.game, pockemon)
                        if isinstance(pockemon, PockemonCard)
                        else card.use(self.game)
                    )
                    for card, pockemon in use_goods
                ]

        i = self.select_action(selection, action)
        action[i]()
        logger.info(
            f"【{self.name}】{selection[i]}を使用しました"
            if i != 0
            else "グッズカードは使用しませんでした"
        )

    def use_trainer_select(self):
        trainer_cards: list[tuple[TrainerCard, PockemonCard | None]] = []
        for card in self.hand_trainer:
            if use_list := card.can_use(self.game):
                if use_list is True:
                    trainer_cards.append((card, None))
                else:
                    trainer_cards.extend([(card, pockemon) for pockemon in use_list])

        # 使用するかどうかの選択肢
        selection = {}
        action = {}
        manage_duplicates = set()

        # 使用しない選択肢を追加
        selection[len(selection)] = "トレーナーカードを使用しない"
        action[len(action)] = lambda: None

        # 各トレーナーカード単体での使用
        for card, target in trainer_cards:
            if (card.name, id(target)) in manage_duplicates:
                continue
            manage_duplicates.add((card.name, id(target)))
            selection[len(selection)] = (
                f"{card.name}を{target.name}に使う" if target else f"{card.name}を使う"
            )
            action[len(action)] = lambda card=card, target=target: (
                card.use(self.game, target) if target else card.use(self.game)
            )

        i = self.select_action(selection, action)
        logger.debug(selection[i])
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
                    self.prepare_bench_pockemon(self.hand_pockemon[j])
                    for j in reversed(comb)
                ]

        i = self.select_action(selection, action)
        action[i]()

        logger.info(f"【{self.name}】{selection[i]}を実行しました")

    def select_bench(self):
        # active_pockemonが倒されたときの処理
        if len(self.bench) == 0:
            raise GameOverException(self.opponent)

        selection = {}
        action = {}
        for i, card in enumerate(self.bench):
            selection[len(selection)] = f"{card}をアクティブに出す"
            action[len(action)] = (
                lambda card=card: self.prepare_active_pockemon_from_bench(card)
            )

        choice = self.select_action(selection, action)
        action[choice]()

        logger.info(
            f"【{self.name}】{self.active_pockemon.name}をバトル場に配置しました"
        )

    # 選択肢を受け取り行動を選択する。今のところはinput()で選択することに、ここをAI化するのが目標
    def select_action(
        self,
        selection: dict[int, str],
        action: dict[int, Callable] = {},
    ):
        if len(selection) == 1:
            return 0
        logger.info(f"【{self.name}】アクションを選択してください")
        for key, value in selection.items():
            logger.info(f"{key}: {value}")

        if self.is_random:
            # Return random valid index when in random mode
            i = random.choice(list(selection.keys()))
        else:
            while True:
                i = int(input("選択: "))
                if i in selection:
                    break
                else:
                    logger.info("無効な選択です")
        return i

    def set_random(self):
        """Enable random action selection mode"""
        self.is_random = True
        logger.info(f"【{self.name}】ランダムモードを有効化しました")

    def unset_random(self):
        """Disable random action selection mode"""
        self.is_random = False
        logger.info(f"【{self.name}】ランダムモードを無効化しました")

    def save_pkl(self, path=None):
        if path is None:
            path = f"./{self.name}.pkl"

        with open(path, "wb") as f:
            pickle.dump(self, f)

    def load_pkl(self, path=None):
        from game.game import Game

        if path is None:
            path = f"./{self.name}.pkl"

        with open(path, "rb") as f:
            loaded_obj = pickle.load(f)
            for key, value in loaded_obj.__dict__.items():
                if isinstance(value, Game):
                    pass
                elif isinstance(value, Player):
                    pass
                else:
                    setattr(self, key, value)

    def delete_pkl(self):
        os.remove(f"{self.name}.pkl")

    def __str__(self):
        return self.name


if __name__ == "__main__":
    from game.game import Game
