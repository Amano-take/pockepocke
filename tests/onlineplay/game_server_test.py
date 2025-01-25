import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import WebSocket
from fastapi.testclient import TestClient

from server.game_server import ConnectionManager, GameInstance, app

client = TestClient(app)


@pytest.mark.asyncio
async def test_websocket_connection():
    manager = ConnectionManager()
    websocket = AsyncMock(spec=WebSocket)
    websocket.accept = AsyncMock()

    await manager.connect(websocket, "test_client")

    assert "test_client" in manager.active_connections
    websocket.accept.assert_awaited()


@pytest.mark.asyncio
async def test_match_players():
    manager = ConnectionManager()
    manager.set_event_loop()

    with patch(
        "server.game_server.GameInstance.send_game_state", new_callable=AsyncMock
    ) as mock_send_game_state:
        with patch(
            "server.game_server.GameInstance.start_game", new_callable=AsyncMock
        ) as mock_start_game:
            await manager.match_players("player1")
            await manager.match_players("player2")

            assert "player1" not in manager.waiting_players
            assert "player2" not in manager.waiting_players
            assert len(manager.active_games) == 1
            mock_send_game_state.assert_called()
            mock_start_game.assert_called()
