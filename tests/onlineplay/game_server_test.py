
import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi import WebSocket
from unittest.mock import AsyncMock, patch
from server.game_server import app, ConnectionManager

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
    await manager.match_players("player1")
    
    assert "player1" in manager.waiting_players
    
    await manager.match_players("player2")
    
    assert "player1" not in manager.waiting_players
    assert "player2" not in manager.waiting_players
    assert len(manager.active_games) == 1

