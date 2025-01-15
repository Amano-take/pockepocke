# マルチプレイヤー実装のためのクラス設計

## 基本構造

### NetworkPlayer (player.pyの拡張)
```python
class NetworkPlayer(Player):
    def __init__(self, websocket, ...):
        super().__init__(...)
        self.websocket = websocket
        
    async def select_action(self, selection, action):
        # WebSocket経由でクライアントに選択肢を送信
        await self.websocket.send_json({
            "type": "action_request",
            "selections": selection
        })
        # クライアントからの応答を待機
        response = await self.websocket.receive_json()
        return response["selected_index"]
```

### GameState (新規作成)
```python
class GameState:
    def __init__(self, game):
        self.game = game
        
    def to_player_view(self, player_id):
        # プレイヤーごとの視点でゲーム状態を返す
        # 手札など非公開情報は該当プレイヤーにのみ公開
        return {
            "active_player": self.game.active_player.name,
            "turn": self.game.turn,
            "your_hand": self._serialize_hand(player_id),
            "your_bench": self._serialize_bench(player_id),
            "opponent_bench": self._serialize_bench(opponent_id),
            # その他の状態...
        }
```

### GameServer (新規作成)
```python
class GameServer:
    def __init__(self):
        self.waiting_players = []
        self.active_games = {}
        
    async def handle_connection(self, websocket):
        # 新規プレイヤー接続処理
        player = await self._create_player(websocket)
        await self._match_player(player)
        
    async def _match_player(self, player):
        if not self.waiting_players:
            self.waiting_players.append(player)
            await player.notify_waiting()
        else:
            opponent = self.waiting_players.pop()
            game = Game()
            game.set_players(player, opponent)
            self.active_games[game.id] = game
            await game.start()
```

## イベントシステム

### GameEvent (新規作成)
```python
class GameEvent:
    def __init__(self, event_type, data):
        self.type = event_type
        self.data = data
        self.timestamp = time.time()

class EventTypes(Enum):
    DRAW_CARD = "draw_card"
    PLAY_CARD = "play_card"
    ADD_ENERGY = "add_energy"
    ATTACK = "attack"
    TURN_START = "turn_start"
    TURN_END = "turn_end"
```

## 通信プロトコル

### メッセージフォーマット
```json
{
    "type": "event_type",
    "data": {
        // イベント固有のデータ
    },
    "timestamp": 1234567890
}
```

### 主要なメッセージタイプ
1. アクション要求
```json
{
    "type": "action_request",
    "data": {
        "selections": {
            "0": "カードを引く",
            "1": "エネルギーを付与"
        }
    }
}
```

2. アクション応答
```json
{
    "type": "action_response",
    "data": {
        "selected_index": 1
    }
}
```

3. 状態更新
```json
{
    "type": "state_update",
    "data": {
        "game_state": {
            // GameState.to_player_viewの結果
        }
    }
}
```

## セキュリティ考慮事項

1. 入力検証
- クライアントからの全入力を検証
- 不正な操作の防止

2. 状態管理
- サーバー側で全ての状態を管理
- クライアントは表示のみを担当

3. 認証
- WebSocket接続時の認証
- セッション管理

## 実装手順

1. 基本クラスの作成
   - NetworkPlayer
   - GameState
   - GameServer
   
2. イベントシステムの実装
   - GameEventの作成
   - イベントハンドラーの実装
   
3. 通信プロトコルの実装
   - WebSocket通信の確立
   - メッセージのシリアライズ/デシリアライズ
   
4. 状態同期の実装
   - 定期的な状態更新
   - 差分更新の最適化
