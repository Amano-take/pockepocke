## アーキテクチャ概要

pockepocke/
├── README.md                  # プロジェクト概要
├── requirements.txt           # 必要なPythonパッケージ
├── main.py                    # メインスクリプト
├── game/                      # ゲームのロジック
│   ├── __init__.py
│   ├── game.py                # Gameクラス
│   ├── player.py              # Playerクラス
│   ├── cards/                 # カード関連
│   │   ├── __init__.py
│   │   ├── pokemon_card.py    # PokemonCardクラス
│   │   ├── tool_card.py       # ToolCardクラス
│   │   └── trainer_card.py    # TrainerCardクラス
│   └── utils.py               # 共通のユーティリティ関数
├── ai/                        # AIプレイヤー関連
│   ├── __init__.py
│   ├── ai_player.py           # AIのロジック
│   └── strategies.py          # 戦略アルゴリズム
├── interface/                 # インターフェース関連
│   ├── __init__.py
│   ├── cli.py                 # テキストベースインターフェース
│   └── web/                   # Webインターフェース
│       ├── __init__.py
│       ├── app.py             # FastAPIアプリ
│       ├── websocket.py       # WebSocketハンドラ
│       └── templates/         # HTMLテンプレート
├── tests/                     # テストコード
│   ├── __init__.py
│   ├── test_game.py           # ゲームロジックのテスト
│   ├── test_ai.py             # AIのテスト
│   ├── test_interface.py      # インターフェースのテスト
│   └── test_websocket.py      # WebSocket通信のテスト
└── docs/                      # ドキュメント
    ├── architecture.md        # 設計に関する詳細
    ├── rules.md               # ゲームルール
    ├── multiplayer_design.md  # マルチプレイヤー設計
    ├── blueprint.md           # 開発ガイドライン
    └── trouble.md             # 技術的課題と解決策

## 主要コンポーネント

### ゲームエンジン
- Gameクラス: ゲームのメインループと状態管理
- Playerクラス: プレイヤーの状態と行動を管理
- カードシステム: ポケモンカード、ツールカード、トレーナーカードの実装

### ネットワーク層
- WebSocketサーバー: リアルタイム通信を処理
- ゲームサーバー: マッチメイキングとゲームセッション管理
- 状態同期: クライアント間のゲーム状態を同期

### クライアント
- Webインターフェース: ゲームのビジュアル表示
- アクション処理: ユーザー入力の処理とサーバーへの送信
- 状態表示: ゲーム状態のリアルタイム更新

## 通信プロトコル

### WebSocketメッセージ形式
