from sqlitestorage.storage import SQLiteStorage
import pytest
import pytest_asyncio
from pytest_lazyfixture import lazy_fixture

from aiogram.contrib.fsm_storage.memory import MemoryStorage

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture()
@pytest.mark.sqlite
async def sqlite_store(options):
    s = SQLiteStorage(**options)
    try:
        yield s
    finally:
        await s.close()
        await s.wait_closed()


@pytest_asyncio.fixture()
async def memory_store():
    yield MemoryStorage()


@pytest.mark.parametrize(
    "store", [
        lazy_fixture('sqlite_store'),
        lazy_fixture('memory_store'),
    ]
)
class TestStorage:
    async def test_set_get(self, store):
        assert await store.get_data(chat='1234') == {}
        await store.set_data(chat='1234', data={'foo': 'bar'})
        assert await store.get_data(chat='1234') == {'foo': 'bar'}

    async def test_reset(self, store):
        await store.set_data(chat='1234', data={'foo': 'bar'})
        await store.reset_data(chat='1234')
        assert await store.get_data(chat='1234') == {}

    async def test_reset_empty(self, store):
        await store.reset_data(chat='1234')
        assert await store.get_data(chat='1234') == {}


@pytest.mark.parametrize(
    "store", [
        lazy_fixture('sqlite_store'),
    ]
)
class TestRedisStorage2:
    async def test_close_and_open_connection(self, store: SQLiteStorage):
        await store.set_data(chat='1234', data={'foo': 'bar'})
        assert await store.get_data(chat='1234') == {'foo': 'bar'}
        await store.close()
        await store.wait_closed()

    @pytest.mark.parametrize(
        "chat_id,user_id,state",
        [
            [12345, 54321, "foo"],
            [12345, 54321, None],
            [12345, None, "foo"],
            [None, 54321, "foo"],
        ],
    )
    async def test_set_get_state(self, chat_id, user_id, state, store):
        await store.reset_state(chat=chat_id, user=user_id, with_data=False)

        await store.set_state(chat=chat_id, user=user_id, state=state)
        s = await store.get_state(chat=chat_id, user=user_id)
        assert s == state

    @pytest.mark.parametrize(
        "chat_id,user_id,data,new_data",
        [
            [12345, 54321, {"foo": "bar"}, {"bar": "foo"}],
            [12345, 54321, None, None],
            [12345, 54321, {"foo": "bar"}, None],
            [12345, 54321, None, {"bar": "foo"}],
            [12345, None, {"foo": "bar"}, {"bar": "foo"}],
            [None, 54321, {"foo": "bar"}, {"bar": "foo"}],
        ],
    )
    async def test_set_get_update_data(self, chat_id, user_id, data, new_data, store):
        await store.reset_state(chat=chat_id, user=user_id, with_data=True)

        await store.set_data(chat=chat_id, user=user_id, data=data)
        d = await store.get_data(chat=chat_id, user=user_id)
        assert d == (data or {})

        await store.update_data(chat=chat_id, user=user_id, data=new_data)
        d = await store.get_data(chat=chat_id, user=user_id)
        updated_data = (data or {})
        updated_data.update(new_data or {})
        assert d == updated_data
