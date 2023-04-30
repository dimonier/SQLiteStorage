from sqlite3 import connect, Connection
from aiogram.dispatcher.storage import BaseStorage
from typing import Any
from json import dumps, loads


class SQLiteStorage(BaseStorage):  # type: ignore
    """
    Simple SQLite based storage for Finite State Machine.

    Intended to replace MemoryStorage for simple cases where you want to keep states
    between bot restarts.
    """

    def __init__(self, db_path: str = "fsm_storage.db"):
        self.db_path = db_path
        self._conn: Connection | None = None
        self._init_db()

    def _init_db(self) -> None:
        conn = connect(self.db_path)
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

    def _get_connection(self) -> Connection:
        if self._conn is None:
            self._conn = connect(self.db_path)
        return self._conn

    async def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    async def wait_closed(self) -> None:
        pass

    async def set_state(self,
                        chat: str | int | None = None,
                        user: str | int | None = None,
                        state: Any | str | None = None,
                        **kwargs: dict[Any, Any]) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO fsm_data
            (key, state, data)
            VALUES (?, ?, COALESCE((SELECT data FROM fsm_data WHERE key = ?), '{}'))
        """, (str(chat) + ":" + str(user), self.resolve_state(state), str(chat) + ":" + str(user)))
        conn.commit()

    async def get_state(self,
                        *,
                        chat: str | int | None = None,
                        user: str | int | None = None,
                        default: str | None = None) -> Any:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT state FROM fsm_data WHERE key = ?", (str(chat) + ":" + str(user),))
        result = cursor.fetchone()
        return result[0] if result else None

    async def set_data(self, *,
                       chat: str | int | None = None,
                       user: str | int | None = None,
                       data: dict[Any, Any] | None = None) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO fsm_data (key, state, data)
            VALUES (?, COALESCE((SELECT state FROM fsm_data WHERE key = ?), ''), ?)
        """, (str(chat) + ":" + str(user), str(chat) + ":" + str(user), dumps(data)))
        conn.commit()

    async def get_data(self, *,
                       chat: str | int | None = None,
                       user: str | int | None = None,
                       default: dict[Any, Any] | None = None) -> Any:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM fsm_data WHERE key = ?", (str(chat) + ":" + str(user),))
        result = cursor.fetchone()
        return loads(result[0]) if result else {}

    async def update_data(self,
                          *,
                          chat: str | int | None = None,
                          user: str | int | None = None,
                          data: dict[Any, Any] | None = None,
                          **kwargs: Any) -> None:
        buffer = await self.get_data(chat=chat, user=user)
        buffer.update(**kwargs)
        await self.set_data(chat=chat, user=user, data=buffer | data if data else buffer)

    async def update_bucket(self,
                            chat: str | int | None = None,
                            user: str | int | None = None,
                            bucket: dict[Any, Any] | None = None,
                            **kwargs: dict[Any, Any]) -> None:
        pass

    async def set_bucket(self,
                         chat: str | int | None = None,
                         user: str | int | None = None,
                         bucket: dict[Any, Any] | None = None) -> None:
        pass

    async def get_bucket(self,
                         chat: str | int | None = None,
                         user: str | int | None = None,
                         default: dict[Any, Any] | None = None) -> dict[Any, Any] | None:
        pass

