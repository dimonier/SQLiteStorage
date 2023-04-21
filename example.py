from aiogram.dispatcher.storage import FSMContext
from aiogram import types

from sqlitestorage.sqlite import SQLiteStorage

# Usage example
async def on_start(message: types.Message):
    fsm_storage = SQLiteStorage()
    fsm_context = FSMContext(dp, fsm_storage)

    # Set state
    await fsm_context.set_state("test_state")
    # Set data
    await fsm_context.set_data({"key": "value"})
    # Get state
    state = await fsm_context.get_state()
    # Get data
    data = await fsm_context.get_data()
    print(state, data)

    # Reset data
    await fsm_context.reset_data()
    # Finish the state
    await fsm_context.finish()

    await message.answer("Done!")
