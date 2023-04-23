import sqlite3
from aiogram.dispatcher.storage import BaseStorage
from typing import Any, Dict, Optional, Tuple
import json
import typing

class SQLiteStorage(BaseStorage):
    """
    Simple SQLite based storage for Finite State Machine.

    Intended to replace MemoryStorage for simple cases where you want to keep states
    between bot restarts.
    """

    async def update_data(self,
                          *,
                          chat: typing.Union[str, int, None] = None,
                          user: typing.Union[str, int, None] = None,
                          data: typing.Dict = None,
                          **kwargs):
        existing_data = await self.get_data(chat=chat, user=user)
        if data:
            existing_data.update(data)
        existing_data.update(**kwargs)

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO fsm_data (key, state, data)
            VALUES (?, COALESCE((SELECT state FROM fsm_data WHERE key = ?), '{}'), ?)
        """, (str(chat) + ":" + str(user), str(chat) + ":" + str(user), json.dumps(existing_data)))
        conn.commit()

    async def update_bucket(self, *, chat: typing.Union[str, int, None] = None,
                            user: typing.Union[str, int, None] = None, bucket: typing.Dict = None, **kwargs):
        pass

    async def set_bucket(self, *, chat: typing.Union[str, int, None] = None, user: typing.Union[str, int, None] = None,
                         bucket: typing.Dict = None):
        pass

    async def get_bucket(self, *, chat: typing.Union[str, int, None] = None, user: typing.Union[str, int, None] = None,
                         default: typing.Optional[dict] = None) -> typing.Dict:
        pass

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

    async def set_state(self, *,
                        chat: typing.Union[str, int, None] = None,
                        user: typing.Union[str, int, None] = None,
                        state: typing.Optional[typing.AnyStr] = None,
                        **kwargs):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO fsm_data
            (key, state, data)
            VALUES (?, ?, COALESCE((SELECT data FROM fsm_data WHERE key = ?), '{}'))
        """, (str(chat) + ":" + str(user), state, str(chat) + ":" + str(user)))
        conn.commit()

    async def get_state(self,
                        *,
                        chat: str | int | None = None,
                        user: str | int | None = None,
                        default: str | None = None) -> typing.Coroutine[Any, Any, str | None]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT state FROM fsm_data WHERE key = ?", (str(chat) + ":" + str(user),))
        result = cursor.fetchone()
        return result[0] if result else None

    async def set_data(self, *,
                       chat: typing.Union[str, int, None] = None,
                       user: typing.Union[str, int, None] = None,
                       data: typing.Dict = None):
        conn = self._get_connection()
        cursor = conn.cursor()
        print(f'data: {json.dumps(data)}')
        print(f'key: {str(chat) + ":" + str(user)}')
        cursor.execute("""
            INSERT OR REPLACE INTO fsm_data (data, key)
            VALUES (?, ?)
        """, (json.dumps(data), str(chat) + ":" + str(user)))
        conn.commit()

    async def get_data(self, *,
                       chat: typing.Union[str, int, None] = None,
                       user: typing.Union[str, int, None] = None,
                       default: typing.Optional[typing.Dict] = None) -> typing.Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM fsm_data WHERE key = ?", (str(chat) + ":" + str(user),))
        result = cursor.fetchone()
        data = result[0] if result else {}
        print(f'data: {data}')
        print(f'key: {str(chat) + ":" + str(user)}')
        return json.loads(result[0]) if result else {}

    async def reset_data(self, *,
                         chat: typing.Union[str, int, None] = None,
                         user: typing.Union[str, int, None] = None):
        await self.set_data(chat=chat, user=user, data={})
