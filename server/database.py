import sqlite3
from pathlib import Path
import json
from typing import List, Optional

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

    # 既存のテーブルのカラム情報を取得
    c.execute("PRAGMA table_info(deck_ratings)")
    columns = [column[1] for column in c.fetchall()]

    # デッキレーティングテーブルの作成または更新
    if not columns:
        # テーブルが存在しない場合は新規作成
        c.execute(
            """
            CREATE TABLE deck_ratings (
                deck_id INTEGER PRIMARY KEY,
                rating FLOAT NOT NULL DEFAULT 1500,
                games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence_score FLOAT DEFAULT 0,
                reference_score FLOAT DEFAULT 0,
                FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE
            )
        """
        )
    elif "reference_score" not in columns:
        # reference_scoreカラムが存在しない場合は追加
        c.execute("ALTER TABLE deck_ratings ADD COLUMN reference_score FLOAT DEFAULT 0")

    conn.commit()
    conn.close()


def save_deck_to_db(client_id: str, deck_name: str, cards: list, energy: str) -> bool:
    """デッキをデータベースに保存"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()

        # デッキを保存
        c.execute(
            "INSERT INTO decks (client_id, name, cards, energy) VALUES (?, ?, ?, ?)",
            (client_id, deck_name, json.dumps(cards), energy),
        )

        # 新しく作成されたデッキのIDを取得
        deck_id = c.lastrowid

        # デッキレーティングの初期値を設定
        c.execute(
            "INSERT INTO deck_ratings (deck_id, rating, confidence_score) VALUES (?, 1500, 0)",
            (deck_id,),
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
            """
            SELECT d.id, d.name, d.cards, d.energy, d.created_at,
                   COALESCE(r.rating, 1500) as rating,
                   COALESCE(r.games_played, 0) as games_played,
                   COALESCE(r.wins, 0) as wins,
                   COALESCE(r.confidence_score, 0) as confidence_score,
                   COALESCE(r.reference_score, 0) as reference_score,
                   r.last_updated
            FROM decks d
            LEFT JOIN deck_ratings r ON d.id = r.deck_id
            WHERE d.client_id = ?
            ORDER BY d.created_at DESC
            """,
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
                    "rating": row[5],
                    "games_played": row[6],
                    "wins": row[7],
                    "confidence_score": row[8],
                    "reference_score": row[9],
                    "last_updated": row[10],
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

        # デッキの削除（CASCADE制約によりレーティングも自動的に削除されます）
        c.execute(
            "DELETE FROM decks WHERE id = ? AND client_id = ?", (deck_id, client_id)
        )

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting deck: {e}")
        return False


def update_deck_rating(
    deck_id: int,
    rating: float,
    won: Optional[bool] = None,
    reference_score: Optional[float] = None,
    games_played: Optional[int] = None,
    wins: Optional[int] = None,
) -> bool:
    """デッキのレーティングを更新"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()

        if won is not None:
            c.execute(
                """
                UPDATE deck_ratings
                SET rating = ?,
                    games_played = COALESCE(?, games_played + 1),
                    wins = COALESCE(?, wins + ?),
                    confidence_score = CASE
                        WHEN COALESCE(?, games_played) < 10 THEN (COALESCE(?, games_played) + 1) * 10
                        ELSE 100
                    END,
                    last_updated = CURRENT_TIMESTAMP
                WHERE deck_id = ?
                """,
                (
                    rating,
                    games_played,
                    wins,
                    1 if won else 0,
                    games_played,
                    games_played,
                    deck_id,
                ),
            )
        else:
            update_query = "UPDATE deck_ratings SET rating = ?"
            params = [rating]

            if reference_score is not None:
                update_query += ", reference_score = ?"
                params.append(reference_score)

            if games_played is not None:
                update_query += ", games_played = ?"
                params.append(games_played)

            if wins is not None:
                update_query += ", wins = ?"
                params.append(wins)

            update_query += ", last_updated = CURRENT_TIMESTAMP WHERE deck_id = ?"
            params.append(deck_id)

            c.execute(update_query, params)

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating deck rating: {e}")
        return False


def get_all_client_ids() -> List[str]:
    """データベースからすべてのユニークなクライアントIDを取得"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()

        c.execute("SELECT DISTINCT client_id FROM decks")
        client_ids = [row[0] for row in c.fetchall()]

        conn.close()
        return client_ids
    except Exception as e:
        print(f"Error getting client IDs: {e}")
        return []


def get_all_decks() -> list:
    """全てのデッキ一覧を取得"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()

        c.execute(
            """
            SELECT d.id, d.name, d.cards, d.energy, d.created_at, d.client_id,
                   COALESCE(r.rating, 1500) as rating,
                   COALESCE(r.games_played, 0) as games_played,
                   COALESCE(r.wins, 0) as wins,
                   COALESCE(r.confidence_score, 0) as confidence_score,
                   COALESCE(r.reference_score, 0) as reference_score,
                   r.last_updated
            FROM decks d
            LEFT JOIN deck_ratings r ON d.id = r.deck_id
            ORDER BY d.created_at DESC
            """
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
                    "client_id": row[5],
                    "rating": row[6],
                    "games_played": row[7],
                    "wins": row[8],
                    "confidence_score": row[9],
                    "reference_score": row[10],
                    "last_updated": row[11],
                }
            )

        conn.close()
        return decks
    except Exception as e:
        print(f"Error getting all decks from database: {e}")
        return []


# データベースの初期化
init_db()
