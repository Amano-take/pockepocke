## architecture

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
│   └── web/                   # Webインターフェース（必要なら）
│       ├── __init__.py
│       ├── app.py             # FastAPIやFlaskアプリ
│       └── templates/         # HTMLテンプレート
├── tests/                     # テストコード
│   ├── __init__.py
│   ├── test_game.py           # ゲームロジックのテスト
│   ├── test_ai.py             # AIのテスト
│   └── test_interface.py      # インターフェースのテスト
└── docs/                      # ドキュメント
    ├── architecture.md        # 設計に関する詳細
    └── rules.md               # ゲームルール
