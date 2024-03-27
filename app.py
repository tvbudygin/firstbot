from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import TG_token
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import json
import requests

currencies = ['USD', 'EUR', 'GBP', 'RUB']

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


@dp.message_handler(commands=['currency'])
async def process_start_command(message: types.Message):
    current_user = message.from_user.username
    photo = open('static/cur.png', 'rb')
    await bot.send_photo(message.chat.id, photo,
                         caption=f"Здравствуйте, {current_user}! Примеры правильного ввода валюты")
    photo.close()


@dp.callback_query_handler(lambda query: query.data == 'course')
async def process_start_command(callback_query: types.Message):
    markup = InlineKeyboardMarkup(row_width=4)
    lst = []
    for cur_from in currencies:
        for cur_to in currencies:
            if cur_from != cur_to:
                # if cur_from == "RUB":
                #     markup.row(InlineKeyboardButton(f'{cur_from}->{cur_to}', callback_data=f"{cur_from}{cur_to}"))
                # else:
                lst.append(InlineKeyboardButton(f'{cur_from}->{cur_to}', callback_data=f"{cur_from}{cur_to}"))
    markup.add(*lst)
    current_user = callback_query.from_user.username
    await callback_query.message.edit_text(f"Hello, {current_user}!", reply_markup=markup)


@dp.callback_query_handler(lambda query: query.data.upper() == query.data and len(query.data) == 6)
async def process_text(callback_query: types.CallbackQuery):
    text_from_btm = callback_query.data
    data = requests.get(
        f"https://currate.ru/api/?get=rates&pairs={text_from_btm}&key=13872f7e02ced0870781b3c3189439eb").json()
    currency = data.get("data").get(text_from_btm)
    await callback_query.message.answer(f"{text_from_btm[:3]}->{text_from_btm[3:]}: {currency}")


@dp.callback_query_handler(lambda query: query.data in {"currency"})
async def process_text(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(f"Введите сумму:")
    await Form.sum_state.set()

@dp.message_handler(state=Form.sum_state)
async def city(message: types.Message, state: FSMContext):
    summ = message.text
    try:
        float(summ)
        async with state.proxy() as data:
            data['summ'] = summ
        await message.answer(f"Введите вашу валюту")
        await Form.cur_state.set()
    except ValueError:
        await state.finish()
        await message.answer(f"Вы дурак! ввели неверно /start")



@dp.message_handler(state=Form.cur_state)
async def city(message: types.Message, state: FSMContext):
    valuta = message.text
    async with state.proxy() as data:
        data['valuta'] = valuta.upper()
    await message.answer(f"Введите валюту для перевода")
    await Form.cur1_state.set()


@dp.message_handler(state=Form.cur1_state)
async def city(message: types.Message, state: FSMContext):
    valuta_2 = message.text.upper()
    async with state.proxy() as data:
        summ = data.get('summ')
        valuta = data.get("valuta")
    await state.finish()
    req = requests.get(
        f"https://currate.ru/api/?get=rates&pairs={valuta}{valuta_2}&key=13872f7e02ced0870781b3c3189439eb")
    if req.status_code == 200:
        data = req.json()
        try:
            currency = data.get("data").get(f"{valuta}{valuta_2}")
            await message.answer(f"{valuta_2}: {float(currency) * float(summ)}")
        except AttributeError as e:
            await message.answer(f"Вы дурак! ввели неверно /start")
        # except ZeroDivisionError:
        #     await message.answer(f"Вы дурак! ввели неверно /start")
    # data = req.json()
    # if data.get("status") == 200:
    #     currency = data.get("data").get(f"{valuta}{valuta_2}")
    #     await message.answer(f"{valuta_2}: {float(currency) * float(summ)}")
    # else:
    #     await message.answer(f"Вы дурак! ввели неверно /start")


if __name__ == '__main__':
    executor.start_polling(dp)
