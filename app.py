from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import TG_token
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import json
import requests

bot = Bot(token=TG_token)
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    sum_state = State()
    cur_state = State()
    cur1_state = State()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    markup = InlineKeyboardMarkup()
    btm1 = InlineKeyboardButton('View the course', callback_data="course")
    btm2 = InlineKeyboardButton('Enter currency', callback_data="currency")
    markup.add(btm1, btm2)
    current_user = message.from_user.username
    await message.answer(f"Hello, {current_user}!", reply_markup=markup)

@dp.message_handler(commands=['fast'])
async def process_start_command(message: types.Message):
    current_user = message.from_user.username
    await message.answer(f"Здравствуйте,{current_user}! Примеры правильного ввода валюты")
    photo = open('path_to_your_photo.jpg', 'rb')
    await bot.send_photo(message.chat.id, photo, caption='Here is your photo!')
    photo.close()


@dp.callback_query_handler(lambda query: query.data == 'course')
async def process_start_command(callback_query: types.Message):
    markup = InlineKeyboardMarkup()
    btm1 = InlineKeyboardButton('USD->EUR', callback_data="USDEUR")
    btm2 = InlineKeyboardButton('EUR->RUB', callback_data="EURRUB")
    btm3 = InlineKeyboardButton('AED->RUB', callback_data="AEDRUB")
    markup.add(btm1, btm2, btm3)
    current_user = callback_query.from_user.username
    await callback_query.message.edit_text(f"Hello, {current_user}!", reply_markup=markup)


@dp.callback_query_handler(lambda query: query.data in {"EURRUB", "USDEUR", "AEDRUB", "RUBAED"})
async def process_text(callback_query: types.CallbackQuery):
    text_from_btm = callback_query.data
    data = requests.get(
        "https://currate.ru/api/?get=rates&pairs=USDEUR,EURRUB,AEDRUB,RUBAED&key=13872f7e02ced0870781b3c3189439eb").json()
    currency = data.get("data").get(text_from_btm)
    await callback_query.message.answer(f"{text_from_btm}: {currency}")


@dp.callback_query_handler(lambda query: query.data in {"currency"})
async def process_text(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(f"Введите сумму:")
    await Form.sum_state.set()


@dp.message_handler(state=Form.sum_state)
async def city(message: types.Message, state: FSMContext):
    summ = message.text
    async with state.proxy() as data:
        data['summ'] = summ
    await message.answer(f"Введите вашу валюту")
    await Form.cur_state.set()


@dp.message_handler(state=Form.cur_state)
async def city(message: types.Message, state: FSMContext):
    valuta = message.text
    async with state.proxy() as data:
        data['valuta'] = valuta
    await message.answer(f"Введите валюту для перевода")
    await Form.cur1_state.set()


@dp.message_handler(state=Form.cur1_state)
async def city(message: types.Message, state: FSMContext):
    valuta_2 = message.text
    async with state.proxy() as data:
        summ = data.get('summ')
        valuta = data.get("valuta")
    print(f"https://currate.ru/api/?get=rates&pairs={valuta}{valuta_2}&key=13872f7e02ced0870781b3c3189439eb")
    data = requests.get(
        f"https://currate.ru/api/?get=rates&pairs={valuta}{valuta_2}&key=13872f7e02ced0870781b3c3189439eb").json()
    currency = data.get("data").get(f"{valuta}{valuta_2}")
    await message.answer(f"{valuta_2}: {float(currency) * float(summ)}")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp)
