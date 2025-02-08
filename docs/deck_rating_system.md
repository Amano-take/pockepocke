# デッキ評価システム設計ドキュメント

## 1. 概要
デッキの強さを自動的に評価し、0-100のスコアを算出するシステム。AI同士の対戦シミュレーションを通じて、デッキの性能を客観的に評価します。

## 2. アーキテクチャ
```python
ratings/
├── rating_system.py      # Eloレーティング実装
├── deck_evaluator.py     # デッキ評価ロジック
└── simulation_manager.py # シミュレーション管理
```

## 3. コアコンポーネント

### 3.1 レーティングシステム（EloRating）
- 初期レーティング: 1500
- K係数: 32（レーティング変動の大きさを制御）
- スケーリング: 1000-2000のレーティングを0-100にマッピング

### 3.2 シミュレーションマネージャー
- 非同期処理によるバックグラウンドシミュレーション
- 新規デッキ登録時に自動評価開始
- 既存の評価済みデッキとの対戦を実施

### 3.3 データベース拡張
```sql
CREATE TABLE deck_ratings (
    deck_id INTEGER PRIMARY KEY,
    rating FLOAT NOT NULL DEFAULT 1500,
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score FLOAT DEFAULT 0
);
```

## 4. 評価プロセス

1. **初期評価**
   - 新規デッキ登録時に初期レーティング（1500）を付与
   - 信頼度スコア（confidence_score）を0に設定

2. **シミュレーション実行**
   - 既存の評価済みデッキから対戦相手を選択
   - AI/rulebase_playerによる対戦実施
   - 各デッキ10回以上の対戦を実施

3. **レーティング更新**
   - 勝敗結果に基づきEloレーティングを更新
   - 対戦回数に応じて信頼度スコアを更新

4. **表示スコア算出**
   ```python
   display_score = max(0, min(100, (rating - 1000) / 10))
   ```

## 5. フロントエンド統合

### 5.1 デッキ一覧表示の拡張
```html
<div class="deck-info">
    <p>強さ: <span class="deck-rating">${calculateDisplayScore(deck.rating)}</span>/100</p>
    <p>評価信頼度: ${formatConfidence(deck.confidence_score)}</p>
</div>
```

### 5.2 視覚的表現
- レーティングに応じた色分け（赤：強い、青：弱い）
- 信頼度に応じた表示（★マークなど）

## 6. 実装フェーズ

1. データベース拡張
2. レーティングシステム実装
3. シミュレーションマネージャー実装
4. APIエンドポイント追加
5. フロントエンド統合
6. テストとチューニング

## 7. 将来の拡張性

- 定期的な再評価システム
- デッキタイプの分類と相性評価
- メタ環境の分析機能
