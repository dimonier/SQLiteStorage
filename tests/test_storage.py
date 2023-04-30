from aiogram.dispatcher.storage import BaseStorage


async def test_set_get(
        storage: BaseStorage
) -> None:
    assert await storage.get_data() == {}
    await storage.set_data(data={'foo': 'bar'})
    assert await storage.get_data() == {'foo': 'bar'}


async def test_reset(
        storage: BaseStorage
) -> None:
    await storage.set_data(data={'foo': 'bar'})
    await storage.set_state(state='SECOND')

    await storage.reset_data()
    assert await storage.get_state() == 'SECOND'
    await storage.set_data(data={'foo': 'bar'})

    await storage.reset_state()
    assert await storage.get_data() == {'foo': 'bar'}


async def test_reset_empty(
    storage: BaseStorage
) -> None:
    await storage.reset_data()
    assert await storage.get_data() == {}