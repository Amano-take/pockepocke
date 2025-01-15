from typing import Dict, List, Optional
import asyncio
import logging
import uuid
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from enum import Enum

from game.game import Game
from game.player import Player
from game.deck import Deck

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.waiting_players: List[str] = []
        self.active_games: Dict[str, "GameInstance"] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.waiting_players:
            self.waiting_players.remove(client_id)
        logger.info(f"Client {client_id} disconnected")

    async def match_players(self, client_id: str):
        """プレイヤーのマッチメイキングを行う"""
        if not self.waiting_players:
            self.waiting_players.append(client_id)
            await self.send_personal_message(
                {"type": "waiting", "message": "対戦相手を待っています..."}, client_id
            )
        else:
            opponent_id = self.waiting_players.pop(0)
            game_id = str(uuid.uuid4())
            game_instance = GameInstance(game_id, client_id, opponent_id, self)
            self.active_games[game_id] = game_instance
            await game_instance.start_game()

    async def send_personal_message(self, message: dict, client_id: str):
        """特定のクライアントにメッセージを送信"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)


class GameState:
    """ゲームの状態を管理し、クライアントに送信する形式に変換するクラス"""

    def __init__(self, game: Game):
        self.game = game

    def to_dict(self, player_id: str) -> dict:
        """プレイヤーごとの視点でゲーム状態を辞書形式に変換"""
        player = (
            self.game.player1
            if self.game.player1.name == player_id
            else self.game.player2
        )
        opponent = (
            self.game.player2
            if self.game.player1.name == player_id
            else self.game.player1
        )

        return {
            "game_id": str(uuid.uuid4()),  # 一時的なID
            "turn": self.game.turn,
            "active_player": self.game.active_player.name,
            "your_info": {
                "name": player.name,
                "hand_size": len(player.hand_pockemon)
                + len(player.hand_goods)
                + len(player.hand_trainer),
                "deck_size": len(player.deck.cards),
                "active_pokemon": (
                    self._serialize_pokemon(player.active_pockemon)
                    if player.active_pockemon
                    else None
                ),
                "bench": [self._serialize_pokemon(p) for p in player.bench],
            },
            "opponent_info": {
                "name": opponent.name,
                "hand_size": len(opponent.hand_pockemon)
                + len(opponent.hand_goods)
                + len(opponent.hand_trainer),
                "deck_size": len(opponent.deck.cards),
                "active_pokemon": (
                    self._serialize_pokemon(opponent.active_pockemon)
                    if opponent.active_pockemon
                    else None
                ),
                "bench": [self._serialize_pokemon(p) for p in opponent.bench],
            },
        }

    def _serialize_pokemon(self, pokemon) -> dict:
        """ポケモンの情報を辞書形式に変換"""
        if pokemon is None:
            return None
        return {
            "name": pokemon.name,
            "hp": pokemon.hp,
            "max_hp": pokemon.max_hp,
            "energies": [e.name for e in pokemon.energies],
        }


class GameInstance:
    """進行中のゲームインスタンスを管理するクラス"""

    def __init__(
        self, game_id: str, player1_id: str, player2_id: str, manager: ConnectionManager
    ):
        self.game_id = game_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.manager = manager
        self.game = Game()
        self.state = None

    async def start_game(self):
        """ゲームを開始する"""
        # プレイヤーオブジェクトの作成（仮のデッキを使用）
        player1 = NetworkPlayer(self.player1_id, Deck([]), [])
        player2 = NetworkPlayer(self.player2_id, Deck([]), [])

        self.game.set_players(player1, player2)
        self.state = GameState(self.game)

        # 両プレイヤーにゲーム開始を通知
        start_message = {
            "type": "game_start",
            "game_id": self.game_id,
            "timestamp": datetime.now().isoformat(),
        }
        await self._broadcast_to_players(start_message)

        # 初期状態を送信
        await self._send_game_state()

    async def _broadcast_to_players(self, message: dict):
        """両プレイヤーにメッセージを送信"""
        await self.manager.send_personal_message(message, self.player1_id)
        await self.manager.send_personal_message(message, self.player2_id)

    async def _send_game_state(self):
        """各プレイヤーに現在のゲーム状態を送信"""
        await self.manager.send_personal_message(
            {"type": "state_update", "state": self.state.to_dict(self.player1_id)},
            self.player1_id,
        )
        await self.manager.send_personal_message(
            {"type": "state_update", "state": self.state.to_dict(self.player2_id)},
            self.player2_id,
        )


class NetworkPlayer(Player):
    """ネットワーク経由でプレイするプレイヤークラス"""

    def __init__(self, client_id: str, deck: Deck, energies: list):
        super().__init__(deck, energies)
        self.client_id = client_id
        self.name = client_id  # 一時的にクライアントIDを名前として使用

    async def select_action(
        self, selection: Dict[int, str], action: Dict[int, callable]
    ) -> int:
        """WebSocket経由でクライアントにアクション選択を要求"""
        # この実装は後で追加
        # とりあえずデフォルトの選択（0）を返す
        return 0


# FastAPIアプリケーション
app = FastAPI()
manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        await manager.match_players(client_id)
        while True:
            data = await websocket.receive_json()
            # メッセージ処理のロジックをここに実装
    except WebSocketDisconnect:
        manager.disconnect(client_id)
