from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import TG_token
import json

bot = Bot(token=TG_token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    markup = InlineKeyboardMarkup()
    btm1 = InlineKeyboardButton('text1', callback_data="text1")
    btm2 = InlineKeyboardButton('text2', callback_data="text2")
    markup.add(btm1, btm2)
    current_user = message.from_user.username
    await message.answer(f"Hello, {current_user}!", reply_markup=markup)


@dp.callback_query_handler(lambda query: query.data in {"text2", "text1"})
async def process_text(callback_query: types.CallbackQuery):
    with open("x12345.json", "w") as f:
        json.dump(dict(callback_query), f)
    text = callback_query.data
    await callback_query.message.answer(f"Hello, {text}")


if __name__ == '__main__':
    executor.start_polling(dp)
