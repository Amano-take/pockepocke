import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import uuid
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from game.deck import Deck
from game.energy import Energy
from game.game import Game
from game.player import Player
from game.cards import POKEMON_CARDS, GOODS_CARDS, TRAINER_CARDS
from server.database import save_deck_to_db, get_decks_by_client_id, delete_deck
from ratings.simulation_manager import simulation_manager

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.waiting_players: List[str] = []
        self.active_games: Dict[str, "GameInstance"] = {}
        self.pending_actions: Dict[str, asyncio.Future] = {}
        self.player_decks: Dict[str, dict] = {}

    def set_event_loop(self):
        if not hasattr(self, "event_loop"):
            try:
                self.event_loop = asyncio.get_event_loop()
            except Exception as e:
                print(str(e))

    async def request_action(self, client_id: str, selection: Dict[int, str]) -> int:
        """クライアントにアクション選択を要求し、結果を返す

        Args:
            client_id: クライアントID
            selection: 選択肢の辞書 {index: 表示テキスト}

        Returns:
            選択されたインデックス
        """
        logger.info(f"Requesting action selection from client {client_id}")
        if client_id not in self.active_connections:
            logger.warning(f"Client {client_id} is not connected")
            return 0

        try:
            # 選択肢をクライアントに送信
            await self.send_personal_message(
                {
                    "type": "action_request",
                    "data": {"selections": selection},
                    "timestamp": datetime.now().isoformat(),
                },
                client_id,
            )

            # レスポンス待機用のFutureを作成
            future = self.event_loop.create_future()
            self.pending_actions[client_id] = future

            # タイムアウト付きでレスポンスを待機
            try:
                selected_index = await asyncio.wait_for(future, timeout=30.0)
                if selected_index in selection:
                    return selected_index
                logger.warning(
                    f"Invalid selection index {selected_index} from client {client_id}"
                )
                return 0
            except asyncio.TimeoutError:
                logger.warning(f"Action selection timeout for client {client_id}")
                return 0

        except Exception as e:
            logger.error(f"Error during action selection: {str(e)}")
            return 0

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
            # send_game_state()をメインループに登録
            game_instance.game.is_active = True
            asyncio.create_task(game_instance.send_game_state())
            # 別スレッドでゲームを開始
            self.event_loop.run_in_executor(None, game_instance.start_game)

    async def send_personal_message(self, message: dict, client_id: str):
        """特定のクライアントにメッセージを送信"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {str(e)}")
                self.disconnect(client_id)


class GameState:
    """ゲームの状態を管理し、クライアントに送信する形式に変換するクラス"""

    def __init__(self, game: Game):
        self.game = game

    def to_dict(self, player_id: str) -> dict:
        """プレイヤーごとの視点でゲーム状態を辞書形式に変換"""
        if not self.game or not self.game.active_player:
            return {}

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
            "game_id": str(uuid.uuid4()),
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

    def _serialize_pokemon(self, pokemon) -> dict | None:
        """ポケモンの情報を辞書形式に変換"""
        if pokemon is None:
            return None

        energy_list = []
        for i, count in enumerate(pokemon.energies.energies):
            for _ in range(count):
                energy = Energy(i)
                energy_list.append(str(energy))

        return {
            "name": pokemon.name,
            "hp": pokemon.hp,
            "max_hp": pokemon.max_hp,
            "energies": energy_list,
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
        self.state = GameState(self.game)

        # デッキの設定
        from tests.utils.set_lightning import lightning_deck

        cards1 = lightning_deck()
        cards2 = lightning_deck()
        deck1 = Deck(cards1)
        deck2 = Deck(cards2)
        energies = [Energy.LIGHTNING]

        # プレイヤーの設定
        player1 = NetworkPlayer(self.player1_id, deck1, energies, self.manager)
        player2 = NetworkPlayer(self.player2_id, deck2, energies, self.manager)
        self.game.set_players(player1, player2)
        self.game.active_player = player1

    def start_game(self):
        """ゲームを開始する"""
        try:
            # 両プレイヤーにゲーム開始を通知
            start_message = {
                "type": "game_start",
                "game_id": self.game_id,
                "timestamp": datetime.now().isoformat(),
            }
            future = asyncio.run_coroutine_threadsafe(
                self._broadcast_to_players(start_message), self.manager.event_loop
            )
            print("This place ")
            future.result(timeout=5)  # 5秒タイムアウト

            # 初期手札を配る
            self.game.start()

        except Exception as e:
            logger.error(f"Unexpected error during game start: {str(e)}")
            future = asyncio.run_coroutine_threadsafe(
                self._broadcast_to_players(
                    {
                        "type": "game_error",
                        "message": "ゲームの開始中に予期せぬエラーが発生しました",
                    }
                ),
                self.manager.event_loop,
            )
            future.result(timeout=5.0)

    async def handle_action(self, client_id: str, action_data: dict):
        """クライアントからのアクションを処理"""
        if not self.game:
            return

        player = (
            self.game.player1
            if self.game.player1.name == client_id
            else self.game.player2
        )

    async def _broadcast_to_players(self, message: dict):
        """両プレイヤーにメッセージを送信"""
        await self.manager.send_personal_message(message, self.player1_id)
        await self.manager.send_personal_message(message, self.player2_id)

    async def send_game_state(self):
        """各プレイヤーに現在のゲーム状態を送信"""
        while self.game.is_active:
            if self.state:
                logger.info(f"Sending game state to players in game {self.game_id}")
                await self.manager.send_personal_message(
                    {
                        "type": "state_update",
                        "state": self.state.to_dict(self.player1_id),
                    },
                    self.player1_id,
                )
                await self.manager.send_personal_message(
                    {
                        "type": "state_update",
                        "state": self.state.to_dict(self.player2_id),
                    },
                    self.player2_id,
                )
            await asyncio.sleep(1.0)


class NetworkPlayer(Player):
    """ネットワーク経由でプレイするプレイヤークラス"""

    def __init__(
        self,
        client_id: str,
        deck: Deck,
        energies: List[Energy],
        manager: ConnectionManager,
    ):
        super().__init__(deck, energies)
        self.client_id = client_id
        self.name = client_id
        self.manager = manager

    def select_action(
        self, selection: Dict[int, str], action: Dict[int, Callable[[], None]]
    ) -> int:
        """WebSocket経由でクライアントにアクション選択を要求"""
        if not self.manager or self.client_id not in self.manager.active_connections:
            logger.warning(f"Client {self.client_id} is not connected")
            return 0

        try:
            # ConnectionManagerに保存されたイベントループを使用
            future = asyncio.run_coroutine_threadsafe(
                self.manager.request_action(self.client_id, selection),
                self.manager.event_loop,
            )

            try:
                selected_index = future.result(timeout=30.0)  # 30秒タイムアウト
                # 選択されたアクションが有効か確認
                if selected_index in action:
                    return selected_index
                logger.warning(f"Invalid action index selected: {selected_index}")
                return 0
            except asyncio.TimeoutError:
                logger.warning(f"Action selection timeout for client {self.client_id}")
                return 0
            except Exception as e:
                logger.error(f"Error during action selection: {str(e)}")
                return 0

        except Exception as e:
            logger.error(f"Unexpected error in select_action: {str(e)}")
            return 0


# テンプレートとスタティックファイルの設定
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).parent.parent / "static")),
    name="static",
)

mgr = ConnectionManager()


# メインページの提供
@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# デッキビルダーページの提供
@app.get("/deck-builder")
async def get_deck_builder(request: Request):
    return templates.TemplateResponse("deck_builder.html", {"request": request})


def get_pokemon_type_ja(type_str: str) -> str:
    type_mapping = {
        "grass": "くさ",
        "fire": "ほのお",
        "water": "みず",
        "lightning": "でんき",
        "psychic": "エスパー",
        "fighting": "かくとう",
        "darkness": "あく",
        "metal": "はがね",
        "dragon": "ドラゴン",
        "normal": "ノーマル",
    }
    return type_mapping.get(type_str, type_str)


# カード一覧のAPI
@app.get("/api/cards")
async def get_available_cards():
    """利用可能なカードの一覧を返す"""
    cards = []

    # ポケモンカードの追加
    for card_class in POKEMON_CARDS:
        card = card_class()
        pokemon_type = str(card.type) if hasattr(card, "type") else None
        cards.append(
            {
                "id": card.name,
                "name": card.name,
                "type": (
                    "basic_pokemon" if card.previous_pockemon is None else "pokemon"
                ),
                "hp": card.max_hp,
                "category": "pokemon",
                "pokemon_type": (
                    get_pokemon_type_ja(pokemon_type) if pokemon_type else None
                ),
            }
        )

    # グッズカードの追加
    for card_class in GOODS_CARDS:
        card = card_class()
        cards.append(
            {"id": card.name, "name": card.name, "type": "goods", "category": "goods"}
        )

    # トレーナーカードの追加
    for card_class in TRAINER_CARDS:
        card = card_class()
        cards.append(
            {
                "id": card.name,
                "name": card.name,
                "type": "trainer",
                "category": "trainer",
            }
        )

    return JSONResponse(content=cards)


def validate_deck(deck_data: dict) -> tuple[bool, str]:
    cards = deck_data.get("cards", [])
    energy = deck_data.get("energy")

    if len(cards) != 20:
        return False, f"デッキは20枚である必要があります（現在: {len(cards)}枚）"

    # カードの重複チェック
    card_counts = {}
    for card_id in cards:
        card_counts[card_id] = card_counts.get(card_id, 0) + 1
        if card_counts[card_id] > 2:
            return (
                False,
                f"同じカードは2枚までしか入れられません（{card_id}: {card_counts[card_id]}枚）",
            )

    # 種ポケモンの存在チェック
    has_basic_pokemon = False
    for card_id in cards:
        for card_class in POKEMON_CARDS:
            card = card_class()
            if card.name == card_id and hasattr(card, "is_seed") and card.is_seed:
                has_basic_pokemon = True
                break
        if has_basic_pokemon:
            break

    if not has_basic_pokemon:
        return False, "デッキには最低1枚の種ポケモンが必要です"

    if not energy:
        return False, "エナジーの種類を選択してください"

    return True, "バリデーション成功"


# デッキ一覧ページの提供
@app.get("/decks")
async def get_deck_list(request: Request):
    return templates.TemplateResponse("deck_list.html", {"request": request})


# デッキ一覧の取得API
@app.get("/api/decks")
async def get_decks(request: Request):
    client_id = request.cookies.get("client_id")
    if not client_id:
        return JSONResponse(
            content={"error": "クライアントIDが見つかりません"}, status_code=400
        )

    decks = get_decks_by_client_id(client_id)
    return JSONResponse(content=decks)


# デッキの削除API
@app.delete("/api/decks/{deck_id}")
async def delete_deck_api(deck_id: int, request: Request):
    client_id = request.cookies.get("client_id")
    if not client_id:
        return JSONResponse(
            content={"error": "クライアントIDが見つかりません"}, status_code=400
        )

    if delete_deck(deck_id, client_id):
        return JSONResponse(content={"status": "success"})
    else:
        return JSONResponse(
            content={"error": "デッキの削除に失敗しました"}, status_code=500
        )


# デッキの使用API
@app.post("/api/decks/{deck_id}/use")
async def use_deck(deck_id: int, request: Request):
    client_id = request.cookies.get("client_id")
    if not client_id:
        return JSONResponse(
            content={"error": "クライアントIDが見つかりません"}, status_code=400
        )

    decks = get_decks_by_client_id(client_id)
    target_deck = next((deck for deck in decks if deck["id"] == deck_id), None)

    if not target_deck:
        return JSONResponse(
            content={"error": "デッキが見つかりません"}, status_code=404
        )

    # デッキを使用中に設定
    mgr.player_decks[client_id] = {
        "cards": target_deck["cards"],
        "energy": target_deck["energy"],
    }

    return JSONResponse(content={"status": "success"})


# デッキの保存API（既存のものを修正）
@app.post("/api/save-deck")
async def save_deck(request: Request):
    try:
        data = await request.json()
        client_id = request.cookies.get("client_id")
        if not client_id:
            client_id = str(uuid.uuid4())

        # デッキのバリデーション
        is_valid, message = validate_deck(data)
        if not is_valid:
            return JSONResponse(content={"error": message}, status_code=400)

        # デッキ名の取得（デフォルトは現在の日時）
        deck_name = data.get(
            "name", f"デッキ {datetime.now().strftime('%Y/%m/%d %H:%M')}"
        )

        # デッキをデータベースに保存
        if save_deck_to_db(client_id, deck_name, data["cards"], data["energy"]):
            return JSONResponse(
                content={"status": "success", "message": "デッキを保存しました"}
            )
        else:
            return JSONResponse(
                content={"error": "デッキの保存に失敗しました"}, status_code=500
            )
    except Exception as e:
        logger.error(f"Error saving deck: {str(e)}")
        return JSONResponse(
            content={"error": "デッキの保存中にエラーが発生しました"}, status_code=500
        )


# Modify websocket_endpoint to allow dependency injection for testing
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    mgr.set_event_loop()
    await mgr.connect(websocket, client_id)
    try:
        await mgr.match_players(client_id)
        while True:
            data = await websocket.receive_json()

            # アクションレスポンスの処理
            if data["type"] == "action_response":
                if client_id in mgr.pending_actions:
                    future = mgr.pending_actions.pop(client_id)
                    if not future.done():
                        try:
                            selected_index = int(data.get("selected_index", 0))
                            future.set_result(selected_index)
                        except Exception as e:
                            future.set_exception(e)
                else:
                    # 通常のアクション処理
                    game_instance = next(
                        (
                            game
                            for game in mgr.active_games.values()
                            if game.player1_id == client_id
                            or game.player2_id == client_id
                        ),
                        None,
                    )
                    if game_instance:
                        await game_instance.handle_action(client_id, data)
    except WebSocketDisconnect:
        mgr.disconnect(client_id)
        # 切断時に保留中のアクションをキャンセル
        if client_id in mgr.pending_actions:
            future = mgr.pending_actions.pop(client_id)
            if not future.done():
                future.cancel()


@app.on_event("startup")
async def startup_event():
    """サーバー起動時の処理"""
    # 継続的な評価プロセスを開始
    await simulation_manager.start_continuous_evaluation()


@app.on_event("shutdown")
async def shutdown_event():
    """サーバー終了時の処理"""
    # 評価プロセスを停止
    await simulation_manager.stop_evaluation()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
