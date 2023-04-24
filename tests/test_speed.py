import asyncio
import pytest
import functools
import time
import random
from typing import Callable, Any

from aiogram.dispatcher.storage import BaseStorage


THREADS_COUNT = 200


def async_timed():
    def wrapper(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs) -> Any:
            print(f'\nstarting {func} with args {args} {kwargs}')
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(f'finished {func} in {total:.4f} second(s)')

        return wrapped

    return wrapper


@async_timed()
@pytest.mark.async_timeout(20)
async def test_aiostorage_speed(
        aiostorage: BaseStorage
) -> None:
    chats = [''.join(random.choice('0123456789') for _ in range(8)) for _ in range(THREADS_COUNT)]
    pending = [asyncio.create_task(aiostorage.set_data(chat=chat, data={'foo': 'bar'})) for chat in chats]

    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

#        print(f"Done task count: {len(done)}")
#        print(f"Pending task count: {len(pending)}")

#        for done_task in done:
#            print(await done_task)


@async_timed()
@pytest.mark.async_timeout(40)
async def test_storage_speed(
        storage: BaseStorage
) -> None:
    chats = [''.join(random.choice('0123456789') for _ in range(8)) for _ in range(THREADS_COUNT)]
    pending = [asyncio.create_task(storage.set_data(chat=chat, data={'foo': 'bar'})) for chat in chats]

    while pending:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

