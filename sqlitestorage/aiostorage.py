import asyncio
import aiosqlite
from aiogram.dispatcher.storage import BaseStorage
from typing import Any, Dict, Optional, Tuple
import json
import typing


class AIOSQLiteStorage(BaseStorage):
    """
    Simple SQLite based storage for Finite State Machine.

    Intended to replace MemoryStorage for simple cases where you want to keep states
    between bot restarts.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    @classmethod
    async def create(cls, db_path: str = "fsm_storage.db"):
        self = AIOSQLiteStorage(db_path)
        async with aiosqlite.connect(db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS fsm_data (
                    key TEXT PRIMARY KEY,
                    state TEXT,
                    data TEXT
                )
            """)
            await db.commit()
        return self

    async def set_state(self, *,
                        chat: typing.Union[str, int, None] = None,
                        user: typing.Union[str, int, None] = None,
                        state: typing.Optional[typing.AnyStr] = None,
                        **kwargs):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO fsm_data
                (key, state, data)
                VALUES (?, ?, COALESCE((SELECT data FROM fsm_data WHERE key = ?), '{}'))
            """, (str(chat) + ":" + str(user), state, str(chat) + ":" + str(user)))
            await db.commit()

    async def get_state(self,
                        *,
                        chat: str | int | None = None,
                        user: str | int | None = None,
                        default: str | None = None) -> typing.Coroutine[Any, Any, str | None]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT state FROM fsm_data WHERE key = ?", (str(chat) + ":" + str(user),))
            result = await cursor.fetchone()
            return result[0] if result else None

    async def set_data(self, *,
                       chat: typing.Union[str, int, None] = None,
                       user: typing.Union[str, int, None] = None,
                       data: typing.Dict | None = None):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO fsm_data (key, state, data)
                VALUES (?, COALESCE((SELECT state FROM fsm_data WHERE key = ?), ''), ?)
            """, (str(chat) + ":" + str(user), str(chat) + ":" + str(user), json.dumps(data)))
            await db.commit()

    async def get_data(self, *,
                       chat: typing.Union[str, int, None] = None,
                       user: typing.Union[str, int, None] = None,
                       default: typing.Optional[typing.Dict] = None) -> typing.Dict:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT data FROM fsm_data WHERE key = ?", (str(chat) + ":" + str(user),))
            result = await cursor.fetchone()
            return json.loads(result[0]) if result else {}

    async def reset_data(self, *,
                         chat: typing.Union[str, int, None] = None,
                         user: typing.Union[str, int, None] = None):
        await self.set_data(chat=chat, user=user, data={})

    async def update_data(self,
                          *,
                          chat: typing.Union[str, int, None] = None,
                          user: typing.Union[str, int, None] = None,
                          data: typing.Dict[Any, Any] | None = None,
                          **kwargs: Any) -> None:
        existing_data = await self.get_data(chat=chat, user=user)
        if data:
            existing_data.update(data)
        existing_data.update(**kwargs)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO fsm_data (key, state, data)
                VALUES (?, COALESCE((SELECT state FROM fsm_data WHERE key = ?), '{}'), ?)
            """, (str(chat) + ":" + str(user), str(chat) + ":" + str(user), json.dumps(existing_data)))
            await db.commit()

    async def update_bucket(self,
                            *,
                            chat: typing.Union[str, int, None] = None,
                            user: typing.Union[str, int, None] = None,
                            bucket: typing.Dict | None = None,
                            **kwargs):
        pass

    async def set_bucket(self,
                         *,
                         chat: typing.Union[str, int, None] = None,
                         user: typing.Union[str, int, None] = None,
                         bucket: typing.Dict | None = None) -> None:
        pass

    async def get_bucket(self,
                         *,
                         chat: typing.Union[str, int, None] = None,
                         user: typing.Union[str, int, None] = None,
                         default: typing.Optional[dict] | None = None) -> dict | None:
        pass

