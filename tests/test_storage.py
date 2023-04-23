from aiogram.dispatcher.storage import BaseStorage


async def test_set_get(
        storage: BaseStorage
) -> None:
    assert await storage.get_data(chat='1234') == {}
    await storage.set_data(chat='1234', data={'foo': 'bar'})
    assert await storage.get_data(chat='1234') == {'foo': 'bar'}


async def test_reset(
        storage: BaseStorage
) -> None:
    await storage.set_data(chat='1234', data={'foo': 'bar'})
    await storage.reset_data(chat='1234')
    assert await storage.get_data(chat='1234') == {}


async def test_reset_empty(
    storage: BaseStorage
) -> None:
    await storage.reset_data(chat='1234')
    assert await storage.get_data(chat='1234') == {}