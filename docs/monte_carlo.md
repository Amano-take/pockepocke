## list select_action phase
Active Pokémon Selection:
    The names of Pokémon cards that can be placed on the battlefield.
    Example: "[select_active] Pikachuをバトル場に出す"
Bench Pokémon Selection:
    The names of Pokémon cards that can be placed on the bench.
    Example: "[select_bench] [Bulbasaur, Charmander]をベンチに出す"
Attack Selection:
The names of attacks that can be performed on a target Pokémon.
Example: "[attack] ThunderboltをCharmanderに使用"
Retreat Selection:
Options for retreating or not retreating the active Pokémon.
Example: "[select_retreat] 逃げない"
Energy Attachment Selection:
Options for attaching energy to active or bench Pokémon.
Example: "[select_energy] Pikachuにエネルギーをつける"
Goods Usage Selection:
Options for using goods cards.
Example: "[goods] MonsterBallを使用しました"
Trainer Usage Selection:
Options for using trainer cards.
Example: "[trainer] Potionを使用"
Evolution Selection:
Options for evolving Pokémon.
Example: "[evolve] [Pikachu]を進化"

# モンテカルロ木探索（MCTS）の実装

## 概要
モンテカルロ木探索は、ゲームAIにおける意思決定アルゴリズムです。このプロジェクトでは、ポケモンカードゲームにおいてMCTSを使用して最適な行動を選択します。

## 主要コンポーネント

### MonteCarloPlayerクラス
- 基本クラス: `Player`
- シミュレーション回数: デフォルトで100回
- 主要な機能: ゲーム状態の評価、行動の選択、シミュレーションの実行

### 行動選択プロセス

1. **フェーズの管理**
   - select_active: アクティブポケモンの選択
   - select_bench: ベンチポケモンの選択
   - goods: グッズカードの使用
   - trainer: トレーナーカードの使用
   - evolve: 進化の実行
   - pockemon: 新しいポケモンの配置
   - select_energy: エネルギーの付与
   - feature: 特性の使用
   - select_retreat: 退却の選択
   - attack: 攻撃の実行

2. **行動評価プロセス**
   ```python
   for each action:
       score = 0
       for n_simulations times:
           score += simulate_game()
       average_score = score / n_simulations
   ```

3. **状態評価基準**
   - サイドカードの状況（30%）
   - アクティブポケモンのHP比率（20%）
   - 勝利/敗北条件の確認
   - ベースライン評価（50%）

## シミュレーション詳細

### シミュレーションの流れ
1. 現在の状態をコピー
2. 選択可能な行動をリストアップ
3. 各行動に対してシミュレーションを実行
4. 結果を評価して最適な行動を選択

### 評価スコア
- 勝利: 1.0
- 引き分け: 0.5
- 敗北: 0.0

## 実装の特徴

### 最適化
- 状態のセーブ/ロード機能
- 効率的なシミュレーション
- ランダム性の制御

### 拡張性
- 新しい評価基準の追加が容易
- フェーズの追加/変更が可能
- パラメータの調整が可能

## 使用例

```python
player = MonteCarloPlayer(deck, energy_types, n_simulations=100)
action = player.select_action(selection, action)
```

## 今後の改善点

1. パラメータの最適化
   - シミュレーション回数の調整
   - 評価基準の重み付けの最適化

2. パフォーマンスの向上
   - 並列処理の導入
   - メモリ使用の最適化

3. 評価関数の改善
   - より詳細な状態評価
   - 学習による評価関数の改善
