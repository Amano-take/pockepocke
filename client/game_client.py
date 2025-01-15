import asyncio
import json
import sys
import os
import uuid
import websockets
import threading
from datetime import datetime
from typing import Dict, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from interface.visualizer import Visualizer


class GameClient:
    """WebSocketを使用してサーバーと通信するゲームクライアント"""

    def __init__(self, server_url: str = "ws://localhost:8000"):
        self.server_url = server_url
        self.client_id = str(uuid.uuid4())
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.game_id: Optional[str] = None
        self.visualizer = Visualizer()
        self.running = True
        self.action_event = asyncio.Event()
        self.selected_action = None

    async def connect(self):
        """サーバーに接続"""
        try:
            self.websocket = await websockets.connect(
                f"{self.server_url}/ws/{self.client_id}"
            )
            print("サーバーに接続しました")
            return True
        except Exception as e:
            print(f"接続エラー: {e}")
            return False

    async def disconnect(self):
        """サーバーから切断"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.running = False

    async def run(self):
        """クライアントのメインループ"""
        if not await self.connect():
            return

        try:
            # メッセージ受信ループを開始
            while self.running:
                message = await self.websocket.recv()
                await self.handle_message(json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            print("サーバーとの接続が切断されました")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
        finally:
            await self.disconnect()

    async def handle_message(self, message: dict):
        """サーバーからのメッセージを処理"""
        message_type = message.get("type")

        if message_type == "waiting":
            print(message["message"])

        elif message_type == "game_start":
            self.game_id = message["game_id"]
            print(f"ゲームが開始されました (ID: {self.game_id})")

        elif message_type == "state_update":
            self.update_game_state(message["state"])

        elif message_type == "action_request":
            await self.handle_action_request(message["data"])

    def update_game_state(self, state: dict):
        """ゲーム状態を更新して表示"""
        # TODO: Visualizerを使用してゲーム状態を表示
        print("\n=== ゲーム状態 ===")
        print(f"ターン: {state['turn']}")
        print(f"アクティブプレイヤー: {state['active_player']}")

        # Your info
        print("\nあなたの情報:")
        print(f"名前: {state['your_info']['name']}")
        print(f"手札: {state['your_info']['hand_size']}枚")
        print(f"デッキ: {state['your_info']['deck_size']}枚")
        if state["your_info"]["active_pokemon"]:
            pokemon = state["your_info"]["active_pokemon"]
            print(
                f"場のポケモン: {pokemon['name']} (HP: {pokemon['hp']}/{pokemon['max_hp']})"
            )

        # Opponent info
        print("\n相手の情報:")
        print(f"名前: {state['opponent_info']['name']}")
        print(f"手札: {state['opponent_info']['hand_size']}枚")
        print(f"デッキ: {state['opponent_info']['deck_size']}枚")
        if state["opponent_info"]["active_pokemon"]:
            pokemon = state["opponent_info"]["active_pokemon"]
            print(
                f"場のポケモン: {pokemon['name']} (HP: {pokemon['hp']}/{pokemon['max_hp']})"
            )
        print("==================\n")

    async def handle_action_request(self, data: dict):
        """アクション選択要求を処理"""
        selections = data["selections"]
        print("\n=== アクション選択 ===")
        for idx, description in selections.items():
            print(f"{idx}: {description}")

        # 入力を受け付ける
        while True:
            try:
                choice = int(input("選択してください: "))
                if str(choice) in selections:
                    await self.send_action_response(choice)
                    break
                else:
                    print("無効な選択です")
            except ValueError:
                print("数字を入力してください")

    async def send_action_response(self, selected_index: int):
        """選択したアクションをサーバーに送信"""
        if self.websocket:
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "action_response",
                        "data": {"selected_index": selected_index},
                    }
                )
            )


def main():
    client = GameClient()
    asyncio.get_event_loop().run_until_complete(client.run())


if __name__ == "__main__":
    main()
