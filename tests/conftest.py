from typing import AsyncGenerator

import os
import pytest

from bson import ObjectId
from sqlitestorage.storage import SQLiteStorage
from sqlitestorage.aiostorage import AIOSQLiteStorage


@pytest.fixture()
async def storage() -> AsyncGenerator[SQLiteStorage, None]:
    db_filename = str(ObjectId()) + ".db"
    database = SQLiteStorage(db_path=db_filename)
    try:
        yield database
    finally:
        await database.close()
        await database.wait_closed()
        os.remove(db_filename)


@pytest.fixture()
async def aiostorage() -> AsyncGenerator[SQLiteStorage, None]:
    db_filename = str(ObjectId()) + ".db"
    database = await AIOSQLiteStorage.create(db_path=db_filename)
    try:
        yield database
    finally:
        os.remove(db_filename)
