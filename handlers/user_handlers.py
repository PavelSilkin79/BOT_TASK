import random


from copy import deepcopy

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon import LEXICON
from keyboards.keyboards import  create_inline_kb
from database.database import users_db



router = Router()

class Form(StatesGroup):
    id = State()
    name = State()
    user_answer = State()
    captcha_answer = State()
    language = State()
    user_data = State()



# Этот хэндлер будет срабатывать на команду /start 
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.username

    # Добавляем данные пользователа в словпарь
    users_db[user_id] = {'user_name': user_name}

    await message.answer(text=LEXICON['/start'])
    print(users_db)

# Этот хэндлер будет срабатывать на команду "/help"
# и отправлять пользователю сообщение со списком доступных команд в боте
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=f'{LEXICON['/help']}')

# Этот хэндлер будет срабатывать на команду "/continue"
# и предлогать поьзователю решить капчу
@router.message(Command(commands='continue'))
async def process_continue_command(message: Message, state: FSMContext):
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    operation = random.choice(['+', '-'])
    answer = num1 + num2 if operation == '+' else num1 - num2

    # Сохраняем правильный ответ на капчу в данные пользователя
    await state.set_state(Form.captcha_answer)
    await state.update_data(captcha_answer=answer)
    question = f"What is {num1} {operation} {num2}?"

    await message.answer(text= f'{LEXICON['capcha']}\n{question}')


    # Хендлер для проверки ответа на капчу
@router.message(lambda message: message.text.isdigit(), StateFilter(Form.captcha_answer))
async def check_captcha(message: Message, state: FSMContext):
    user_answer = int(message.text)
    user_data = await state.get_data()

    if user_answer == user_data.get('captcha_answer'):
        await message.answer('✅', reply_markup=create_inline_kb(2, 'en_button', 'ru_button'))
    else:
        await message.answer(text=LEXICON['no'])

# Хендлер для выбора языка
@router.callback_query(lambda callback_query: callback_query.data in ['en_button', 'ru_button'])
async def choose_language(callback_query: types.CallbackQuery, state: FSMContext):
    chosen_language = callback_query.data 
    await state.update_data(language=chosen_language)

    if chosen_language == 'en_button':
        await callback_query.message.answer(text= f'{LEXICON['English']} \n{callback_query.from_user.username}, {LEXICON['English1']}')
    elif chosen_language == 'ru_button':
        await callback_query.message.answer(text= f'{LEXICON['Русский']}\n{callback_query.from_user.username}{LEXICON['Русский1']}')
