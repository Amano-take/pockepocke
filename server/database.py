import sqlite3
from pathlib import Path
import json

DATABASE_PATH = Path(__file__).parent.parent / "data" / "pockepocke.db"


def init_db():
    """データベースとテーブルを初期化"""
    DATABASE_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # デッキテーブルの作成
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            client_id TEXT NOT NULL,
            cards TEXT NOT NULL,
            energy TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()


def save_deck_to_db(client_id: str, deck_name: str, cards: list, energy: str) -> bool:
    """デッキをデータベースに保存"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()

        c.execute(
            "INSERT INTO decks (client_id, name, cards, energy) VALUES (?, ?, ?, ?)",
            (client_id, deck_name, json.dumps(cards), energy),
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving deck to database: {e}")
        return False


def get_decks_by_client_id(client_id: str) -> list:
    """クライアントIDに紐づくデッキ一覧を取得"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()

        c.execute(
            "SELECT id, name, cards, energy, created_at FROM decks WHERE client_id = ? ORDER BY created_at DESC",
            (client_id,),
        )

        decks = []
        for row in c.fetchall():
            decks.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "cards": json.loads(row[2]),
                    "energy": row[3],
                    "created_at": row[4],
                }
            )

        conn.close()
        return decks
    except Exception as e:
        print(f"Error getting decks from database: {e}")
        return []


def delete_deck(deck_id: int, client_id: str) -> bool:
    """デッキを削除"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()

        c.execute(
            "DELETE FROM decks WHERE id = ? AND client_id = ?", (deck_id, client_id)
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting deck: {e}")
        return False


# データベースの初期化
init_db()
