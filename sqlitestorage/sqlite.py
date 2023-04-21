import sqlite3
from aiogram.dispatcher.storage import BaseStorage
from typing import Any, Dict, Optional, Tuple
import json

class SQLiteStorage(BaseStorage):
    """
    Simple SQLite based storage for Finite State Machine.

    Intended to replace MemoryStorage for simple cases where you want to keep states
    between bot restarts.
    """
    def __init__(self, db_path: str = "fsm_storage.db"):
        self.db_path = db_path
        self._conn = None
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fsm_data (
                key TEXT PRIMARY KEY,
                state TEXT,
                data TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _get_connection(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn

    async def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None


    async def wait_closed(self) -> None:
        pass


    async def set_state(self, key: Tuple[int, str], state: Optional[str]) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO fsm_data (key, state, data)
            VALUES (?, ?, COALESCE((SELECT data FROM fsm_data WHERE key = ?), '{}'))
        """, (str(key), state, str(key)))
        conn.commit()

    async def get_state(self, key: Tuple[int, str]) -> Optional[str]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT state FROM fsm_data WHERE key = ?", (str(key),))
        result = cursor.fetchone()
        return result[0] if result else None

    async def set_data(self, key: Tuple[int, str], data: Dict[str, Any]) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO fsm_data (key, state, data)
            VALUES (?, COALESCE((SELECT state FROM fsm_data WHERE key = ?), ''), ?)
        """, (str(key), str(key), json.dumps(data)))
        conn.commit()

    async def get_data(self, key: Tuple[int, str]) -> Dict[str, Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM fsm_data WHERE key = ?", (str(key),))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else {}

    async def reset_data(self, key: Tuple[int, str]) -> None:
        await self.set_data(key, {})
