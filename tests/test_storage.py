from aiogram.dispatcher.storage import BaseStorage


async def test_set_get(
    storage: BaseStorage
) -> None:
    assert await storage.get_data(chat='1234') == {}
    await storage.set_data(chat='1234', data={'foo': 'bar'})
    assert await storage.get_data(chat='1234') == {'foo': 'bar'}
