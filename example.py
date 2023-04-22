from aiogram.dispatcher.storage import FSMContext
from aiogram import types, Dispatcher, Bot

from sqlitestorage.storage import SQLiteStorage

from config import API_TOKEN

bot = Bot(token=API_TOKEN)
storage = SQLiteStorage()
dp = Dispatcher(bot, storage=storage)


# Usage example
async def on_start(message: types.Message, state: FSMContext):
    # Set state
    await state.set_state("test_state")
    # Set data
    await state.set_data({"key": "value"})
    # Get state
    state = await state.get_state()
    # Get data
    print(state)

    await message.answer("Done!")
