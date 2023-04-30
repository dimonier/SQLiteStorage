from aiogram.dispatcher.storage import BaseStorage


async def test_empty_id(
        storage: BaseStorage
) -> None:
    try:
        await storage.get_data() == {}
    except Exception as exp:
        assert isinstance(exp, ValueError)


async def test_set_get(
        storage: BaseStorage
) -> None:
    assert await storage.get_data(chat='1') == {}
    await storage.set_data(chat='1', data={'foo': 'bar'})
    assert await storage.get_data(chat='1') == {'foo': 'bar'}


async def test_update(
        storage: BaseStorage
) -> None:
    await storage.update_data(chat='1', data={'foo': 'bar'})
    assert await storage.get_data(chat='1') == {'foo': 'bar'}

    await storage.update_data(chat='1', **{'first': 'second'})
    assert await storage.get_data(chat='1') == {'foo': 'bar', 'first': 'second'}


async def test_reset(
        storage: BaseStorage
) -> None:
    await storage.set_data(chat='1', data={'foo': 'bar'})
    await storage.set_state(chat='1', state='SECOND')

    await storage.reset_data(chat='1')
    assert await storage.get_state(chat='1') == 'SECOND'
    await storage.set_data(chat='1', data={'foo': 'bar'})

    await storage.reset_state(chat='1')
    assert await storage.get_data(chat='1') == {'foo': 'bar'}


async def test_test_empty(
    storage: BaseStorage
) -> None:
    await storage.reset_data(chat='1')
    assert await storage.get_data(chat='1') == {}

    assert not await storage.get_state(chat='1')
