from __future__ import annotations
from typing import Generator, Tuple, Dict, Callable, Optional, List
from collections import defaultdict
import random
import copy
import math
import logging
from itertools import combinations

from game.player import Player
from game.deck import Deck
from game.energy import Energy
from game.cards.pockemon_card import PockemonCard
from game.exceptions import GameOverException
from game.game import Game

logger = logging.getLogger(__name__)

class MonteCarloNode:
    def __init__(self, parent=None):
        self.parent = parent
        self.children: Dict[int, MonteCarloNode] = {}
        self.visits = 0
        self.value = 0.0
        self.untried_actions: List[int] = []

    def ucb1(self, total_visits: int, exploration: float = math.sqrt(2)) -> float:
        if self.visits == 0:
            return float('inf')
        exploitation = self.value / self.visits
        exploration_term = exploration * math.sqrt(math.log(total_visits) / self.visits)
        return exploitation + exploration_term

    def select_best_child(self, total_visits: int) -> Tuple[int, MonteCarloNode]:
        best_score = float('-inf')
        best_action = None
        best_child = None

        for action, child in self.children.items():
            score = child.ucb1(total_visits)
            if score > best_score:
                best_score = score
                best_action = action
                best_child = child

        return best_action, best_child

class MonteCarloGenePlayer(Player):
    def __init__(self, deck: Deck, energies: list[Energy]):
        super().__init__(deck, energies)
        self.turn_generator = None
        self.simulation_mode = False
        self.mcts_root = None
        self.current_node = None
        self.num_simulations = 100

    def _turn_sequence(self, can_evolve: bool = True) -> Generator[Tuple[Dict[int, str], Dict[int, Callable]], None, None]:
        """ターンの流れをジェネレータとして実装"""
        # Goods cards phase
        selection, actions = self._prepare_goods_options()
        if selection:
            choice = yield selection, actions
            self._execute_goods_action(choice, selection, actions)

        # Trainer cards phase
        selection, actions = self._prepare_trainer_options()
        if selection:
            choice = yield selection, actions
            self._execute_trainer_action(choice, selection, actions)

        # Evolution phase
        if can_evolve:
            selection, actions = self._prepare_evolution_options()
            if selection:
                choice = yield selection, actions
                self._execute_evolution_action(choice, selection, actions)

        # Pokemon placement phase
        selection, actions = self._prepare_pokemon_options()
        if selection:
            choice = yield selection, actions
            self._execute_pokemon_action(choice, selection, actions)

        # Energy attachment phase
        selection, actions = self._prepare_energy_options()
        if selection:
            choice = yield selection, actions
            self._execute_energy_action(choice, selection, actions)

        # Retreat phase
        selection, actions = self._prepare_retreat_options()
        if selection:
            choice = yield selection, actions
            self._execute_retreat_action(choice, selection, actions)

        # Attack phase
        selection, actions = self._prepare_attack_options()
        if selection:
            choice = yield selection, actions
            self._execute_attack_action(choice, selection, actions)

    def _prepare_goods_options(self) -> Tuple[Dict[int, str], Dict[int, Callable]]:
        """グッズカードの選択肢を準備"""
        selection = {}
        action = {}

        # グッズカードを使用しない選択肢
        selection[len(selection)] = "[goods] グッズカードを使用しない"
        action[len(action)] = lambda: None

        # 使用可能なグッズカードの選択肢を追加
        for card in self.hand_goods:
            if use_list := card.can_use(self.game):
                if use_list is True:
                    selection[len(selection)] = f"[goods] {card.name}を使用"
                    action[len(action)] = lambda card=card: card.use(self.game)
                elif isinstance(use_list, list):
                    for target in use_list:
                        selection[len(selection)] = f"[goods] {card.name}を{target.name}に使用"
                        action[len(action)] = lambda card=card, target=target: card.use(self.game, target)

        return selection, action

    def _prepare_trainer_options(self) -> Tuple[Dict[int, str], Dict[int, Callable]]:
        """トレーナーカードの選択肢を準備"""
        selection = {}
        action = {}

        # トレーナーカードを使用しない選択肢
        selection[len(selection)] = "[trainer] トレーナーカードを使用しない"
        action[len(action)] = lambda: None

        # 使用可能なトレーナーカードの選択肢を追加
        for card in self.hand_trainer:
            if use_list := card.can_use(self.game):
                if use_list is True:
                    selection[len(selection)] = f"[trainer] {card.name}を使用"
                    action[len(action)] = lambda card=card: card.use(self.game)
                elif isinstance(use_list, list):
                    for target in use_list:
                        selection[len(selection)] = f"[trainer] {card.name}を{target.name}に使用"
                        action[len(action)] = lambda card=card, target=target: card.use(self.game, target)

        return selection, action

    def _prepare_evolution_options(self) -> Tuple[Dict[int, str], Dict[int, Callable]]:
        """進化の選択肢を準備"""
        selection = {}
        action = {}

        # 進化させない選択肢
        selection[len(selection)] = "[evolve] 進化させない"
        action[len(action)] = lambda: None

        # 進化可能なポケモンの選択肢を追加
        field_pokemon = [self.active_pockemon] + self.bench
        for pokemon in field_pokemon:
            for hand in self.hand_pockemon:
                if hand.previous_pockemon == pokemon.name:
                    selection[len(selection)] = f"[evolve] {pokemon.name}を{hand.name}に進化"
                    action[len(action)] = lambda p=pokemon: self.evolve(p)

        return selection, action

    def _prepare_pokemon_options(self) -> Tuple[Dict[int, str], Dict[int, Callable]]:
        """ポケモンの配置選択肢を準備"""
        selection = {}
        action = {}

        # ポケモンを出さない選択肢
        selection[len(selection)] = "[pockemon] ポケモンを出さない"
        action[len(action)] = lambda: None

        # ベンチに出せるポケモンの選択肢を追加
        if len(self.bench) < 5:
            for card in self.hand_pockemon:
                if card.is_seed:
                    selection[len(selection)] = f"[pockemon] {card.name}をベンチに出す"
                    action[len(action)] = lambda card=card: self.prepare_bench_pockemon(card)

        return selection, action

    def _prepare_energy_options(self) -> Tuple[Dict[int, str], Dict[int, Callable]]:
        """エネルギー付与の選択肢を準備"""
        selection = {}
        action = {}

        # エネルギーを付与しない選択肢
        selection[len(selection)] = "[select_energy] エネルギーをつけない"
        action[len(action)] = lambda: None

        if self.current_energy:
            # アクティブポケモンにエネルギーを付与する選択肢
            if self.active_pockemon:
                selection[len(selection)] = f"[select_energy] {self.active_pockemon.name}にエネルギーをつける"
                action[len(action)] = lambda: self.attach_energy(self.active_pockemon)

            # ベンチポケモンにエネルギーを付与する選択肢
            for pokemon in self.bench:
                selection[len(selection)] = f"[select_energy] {pokemon.name}にエネルギーをつける"
                action[len(action)] = lambda p=pokemon: self.attach_energy(p)

        return selection, action

    def _prepare_retreat_options(self) -> Tuple[Dict[int, str], Dict[int, Callable]]:
        """retreat（逃げる）の選択肢を準備"""
        selection = {}
        action = {}

        # 逃げない選択肢
        selection[len(selection)] = "[select_retreat] 逃げない"
        action[len(action)] = lambda: None

        # 逃げる選択肢を追加
        if self.active_pockemon and self.active_pockemon.can_retreat(self.retreat_cost_buff):
            for bench_pokemon in self.bench:
                cost = self.active_pockemon.retreat_cost - self.retreat_cost_buff
                for comb in combinations(self.active_pockemon.energies.flatten(), cost):
                    selection[len(selection)] = f"[select_retreat] {self.active_pockemon.name}は{bench_pokemon.name}と交代"
                    action[len(action)] = lambda p=bench_pokemon, c=comb: self.retreat(p, list(c))

        return selection, action

    def _prepare_attack_options(self) -> Tuple[Dict[int, str], Dict[int, Callable]]:
        """攻撃の選択肢を準備"""
        selection = {}
        action = {}

        # 攻撃しない選択肢
        selection[len(selection)] = "[attack] ターンを終了する"
        action[len(action)] = lambda: None

        # 使用可能な攻撃の選択肢を追加
        if self.active_pockemon:
            for attack in self.active_pockemon.candidate_attacks():
                for target in attack.target_list(self.game):
                    selection[len(selection)] = f"[attack] {attack.name}を{target.name}に使用"
                    action[len(action)] = lambda a=attack, t=target: self.attack(a, t)

        return selection, action

    def _execute_goods_action(self, choice: int, selection: Dict[int, str], actions: Dict[int, Callable]):
        """選択されたグッズカードのアクションを実行"""
        if choice in actions:
            actions[choice]()

    def _execute_trainer_action(self, choice: int, selection: Dict[int, str], actions: Dict[int, Callable]):
        """選択されたトレーナーカードのアクションを実行"""
        if choice in actions:
            actions[choice]()

    def _execute_evolution_action(self, choice: int, selection: Dict[int, str], actions: Dict[int, Callable]):
        """選択された進化アクションを実行"""
        if choice in actions:
            actions[choice]()

    def _execute_pokemon_action(self, choice: int, selection: Dict[int, str], actions: Dict[int, Callable]):
        """選択されたポケモン配置アクションを実行"""
        if choice in actions:
            actions[choice]()

    def _execute_energy_action(self, choice: int, selection: Dict[int, str], actions: Dict[int, Callable]):
        """選択されたエネルギー付与アクションを実行"""
        if choice in actions:
            actions[choice]()

    def _execute_retreat_action(self, choice: int, selection: Dict[int, str], actions: Dict[int, Callable]):
        """選択されたretreatアクションを実行"""
        if choice in actions:
            actions[choice]()

    def _execute_attack_action(self, choice: int, selection: Dict[int, str], actions: Dict[int, Callable]):
        """選択された攻撃アクションを実行"""
        if choice in actions:
            actions[choice]()

    def select_action(self, selection: dict[int, str], action: dict[int, Callable]) -> int:
        """行動選択のメイン関数"""
        if self.simulation_mode:
            return random.choice(list(selection.keys()))

        if self.turn_generator is None:
            self.turn_generator = self._turn_sequence()
            self.mcts_root = MonteCarloNode()
            self.current_node = self.mcts_root

        # MCTSで次の行動を決定
        choice = self._select_with_mcts(selection)

        try:
            # 選択した行動を実行し、次の状態へ
            next_selection, next_actions = self.turn_generator.send(choice)
            return choice
        except StopIteration:
            self.turn_generator = None
            self.mcts_root = None
            self.current_node = None
            return choice

    def _select_with_mcts(self, selection: Dict[int, str]) -> int:
        """モンテカルロ木探索で行動を選択"""
        if not hasattr(self, 'mcts_root') or self.mcts_root is None:
            self.mcts_root = MonteCarloNode()
            self.current_node = self.mcts_root

        if not self.current_node.untried_actions:
            self.current_node.untried_actions = list(selection.keys())

        for _ in range(self.num_simulations):
            node = self.current_node

            # ジェネレータを含まないゲーム状態のコピーを作成
            state = Game()
            state.turn = self.game.turn
            state.winner = self.game.winner
            state.loser = self.game.loser
            state.is_active = self.game.is_active

            # プレイヤーのジェネレータ関連の属性を一時的にクリア
            player1_turn_gen = self.game.player1.turn_generator
            player2_turn_gen = self.game.player2.turn_generator
            player1_mcts_root = getattr(self.game.player1, 'mcts_root', None)
            player2_mcts_root = getattr(self.game.player2, 'mcts_root', None)
            player1_current_node = getattr(self.game.player1, 'current_node', None)
            player2_current_node = getattr(self.game.player2, 'current_node', None)

            self.game.player1.turn_generator = None
            self.game.player2.turn_generator = None
            if hasattr(self.game.player1, 'mcts_root'):
                self.game.player1.mcts_root = None
            if hasattr(self.game.player2, 'mcts_root'):
                self.game.player2.mcts_root = None
            if hasattr(self.game.player1, 'current_node'):
                self.game.player1.current_node = None
            if hasattr(self.game.player2, 'current_node'):
                self.game.player2.current_node = None

            try:
                # プレイヤーの状態をコピー
                player1 = copy.deepcopy(self.game.player1)
                player2 = copy.deepcopy(self.game.player2)

                state.set_players(player1, player2)
                state.active_player = player1 if self.game.active_player == self.game.player1 else player2
                state.waiting_player = player2 if state.active_player == player1 else player1

                # Selection
                while node.untried_actions == [] and node.children:
                    action, node = node.select_best_child(self.mcts_root.visits)

                # Expansion
                if node.untried_actions:
                    action = random.choice(node.untried_actions)
                    node.untried_actions.remove(action)
                    child = MonteCarloNode(parent=node)
                    node.children[action] = child
                    node = child

                # Simulation
                self.simulation_mode = True
                try:
                    result = self._simulate_from_state(state)
                finally:
                    self.simulation_mode = False

                # Backpropagation
                while node:
                    node.visits += 1
                    node.value += result
                    node = node.parent

            finally:
                # ジェネレータ関連の属性を元に戻す
                self.game.player1.turn_generator = player1_turn_gen
                self.game.player2.turn_generator = player2_turn_gen
                if hasattr(self.game.player1, 'mcts_root'):
                    self.game.player1.mcts_root = player1_mcts_root
                if hasattr(self.game.player2, 'mcts_root'):
                    self.game.player2.mcts_root = player2_mcts_root
                if hasattr(self.game.player1, 'current_node'):
                    self.game.player1.current_node = player1_current_node
                if hasattr(self.game.player2, 'current_node'):
                    self.game.player2.current_node = player2_current_node

        # 最も訪問回数の多い行動を選択
        best_action = max(self.current_node.children.items(),
                         key=lambda x: x[1].visits)[0]
        self.current_node = self.current_node.children[best_action]
        return best_action

    def _simulate_from_state(self, state) -> float:
        """現在の状態からシミュレーションを実行"""
        max_depth = 10  # シミュレーションの最大深さ
        depth = 0

        try:
            while not state.is_finished() and depth < max_depth:
                current_player = state.active_player

                # 各フェーズでランダムな行動を選択して実行
                # Goods phase
                selection, actions = current_player._prepare_goods_options()
                if selection:
                    choice = random.choice(list(selection.keys()))
                    actions[choice]()

                # Trainer phase
                selection, actions = current_player._prepare_trainer_options()
                if selection:
                    choice = random.choice(list(selection.keys()))
                    actions[choice]()

                # Evolution phase
                selection, actions = current_player._prepare_evolution_options()
                if selection:
                    choice = random.choice(list(selection.keys()))
                    actions[choice]()

                # Pokemon placement phase
                selection, actions = current_player._prepare_pokemon_options()
                if selection:
                    choice = random.choice(list(selection.keys()))
                    actions[choice]()

                # Energy phase
                selection, actions = current_player._prepare_energy_options()
                if selection:
                    choice = random.choice(list(selection.keys()))
                    actions[choice]()

                # Retreat phase
                selection, actions = current_player._prepare_retreat_options()
                if selection:
                    choice = random.choice(list(selection.keys()))
                    actions[choice]()

                # Attack phase
                selection, actions = current_player._prepare_attack_options()
                if selection:
                    choice = random.choice(list(selection.keys()))
                    actions[choice]()

                # ターンを終了し、次のプレイヤーに移る
                state.active_player.draw()
                if state.turn > 1:
                    state.active_player.get_energy()
                state.next_turn()
                depth += 1

            # 評価値を返す
            if state.winner == state.active_player:
                return 1.0
            elif state.winner == state.waiting_player:
                return -1.0
            else:
                return self._evaluate_state(state)

        except Exception as e:
            logger.error(f"Simulation error: {e}")
            return 0.0

    def _evaluate_state(self, state) -> float:
        """ゲーム状態を評価"""
        score = 0.0

        # 勝敗による評価
        if state.is_finished():
            if state.winner == self:
                return 1.0
            else:
                return -1.0

        # HPによる評価
        if self.active_pockemon and self.opponent.active_pockemon:
            my_hp_ratio = self.active_pockemon.hp / self.active_pockemon.max_hp
            opp_hp_ratio = self.opponent.active_pockemon.hp / self.opponent.active_pockemon.max_hp
            score += 0.3 * (my_hp_ratio - opp_hp_ratio)
        else:
            # アクティブポケモンがいない場合は不利な状況
            if not self.active_pockemon:
                score -= 0.3
            if not self.opponent.active_pockemon:
                score += 0.3

        # ベンチの状況
        my_bench_count = len(self.bench)
        opp_bench_count = len(self.opponent.bench)
        score += 0.2 * (my_bench_count - opp_bench_count) / 5

        # 手札の状況
        my_hand_count = len(self.hand_pockemon) + len(self.hand_goods) + len(self.hand_trainer)
        opp_hand_count = len(self.opponent.hand_pockemon) + len(self.opponent.hand_goods) + len(self.opponent.hand_trainer)
        score += 0.1 * (my_hand_count - opp_hand_count) / 7

        return score
