from aiogram import types, Dispatcher, Bot, executor
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from sqlitestorage.storage import SQLiteStorage

from config import API_TOKEN

bot = Bot(token=API_TOKEN)
storage = SQLiteStorage()
dp = Dispatcher(bot, storage=storage)


class Phase(StatesGroup):
    START = State()
    SECOND = State()
    FIN = State()


@dp.message_handler(text_startswith='Get values', state=Phase.SECOND)
async def get_value(message: types.Message, state: FSMContext):
    await message.answer(f"State is {await state.get_state()}")
    data = await state.get_data()
    text = '\n'.join(f"{key}: {value}" for key, value in data.items())
    await message.answer(
        f"Values of data is:\n" + text,
        reply_markup=types.ReplyKeyboardRemove()
    )
    await Phase.FIN.set()


@dp.message_handler(state=Phase.FIN)
async def get_value(message: types.Message, state: FSMContext):
    await message.answer(f"State is {await state.get_state()}")
    if message.text == '/start':
        await Phase.START.set()
    else:
        await message.answer("Good bye!")


@dp.message_handler(state=Phase.SECOND)
async def save_value(message: types.Message, state: FSMContext):
    await message.answer(f"State is {await state.get_state()}")
    if '=' not in message.text:
        await message.answer(f"Enter pair of args in format: <key>=<values>")
        return

    key, value = message.text.split('=')
    data = {key: value}
    await state.update_data(**data)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    await message.answer(f"Saved! {key}: {value}.", reply_markup=markup.add(types.KeyboardButton('Get values')))
    await Phase.SECOND.set()


@dp.message_handler(content_types=types.ContentTypes.TEXT, state='*')
async def save_value(message: types.Message, state: FSMContext):
    await message.answer(f"State is {await state.get_state()}")
    if '=' not in message.text:
        await message.answer(f"Enter pair of args in format: <key>=<values>")
        await Phase.START.set()
        return

    key, value = message.text.split('=')
    data = {key: value}
    await state.update_data(data)

    text = f"Saved! {key}: {value}.\nYou can add new pair of key-value to data"
    await message.answer(text)
    await Phase.SECOND.set()


async def shutdown(dp: Dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()
    print('Storage is closed!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)