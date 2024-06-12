import random


from copy import deepcopy

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import CallbackQuery, Message
from lexicon.lexicon import LEXICON
from keyboards.keyboards import game_kb, en_ru_kb, language_keyboard
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database.database import users_db

router = Router()

class Form(StatesGroup):
    id = State()
    name = State()
    user_answer = State()
    captcha_answer = State()
    language = State()
    user_data = State()



# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
 #   if message.from_user.id not in users_db:
  #      users_db[message.from_user.id] = {
   #         'id': message.from_user.id,
    #        'name': message.from_user.first_name

     #   }

    await message.answer(text=LEXICON['/start'])
    print(users_db)

# Этот хэндлер будет срабатывать на команду "/help"
# и отправлять пользователю сообщение со списком доступных команд в боте
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=f'{LEXICON['/help']}')

@router.message(Command(commands='continue'))
async def process_continue_command(message: Message, state: FSMContext):
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    operation = random.choice(['+', '-'])
    if operation == '+': 
        answer = num1 + num2
    else:
        answer = num1 - num2

    # Save captcha answer in user data
    await state.set_state(Form.name)
    await state.update_data(captcha_answer=answer)
    question = f"What is {num1} {operation} {num2}?"

    await message.answer(text= f'{LEXICON['capcha']}\n{question}')


    # Captcha response handler
@router.message(lambda message: message.text.isdigit())
async def check_captcha(message: Message, state: FSMContext):
    user_answer = int(message.text)
    await state.set_state(Form.name)
    user_data = await state.get_data()

    if user_answer == user_data.get('captcha_answer'):
        
        await message.answer('✅', reply_markup=en_ru_kb)
    else:
        await message.answer(text=LEXICON['no'])

# Language selection handler
@router.message(lambda message: message.text in ['English', 'Русский'])
async def choose_language(message: Message, state: FSMContext):
    chosen_language = message.text
    await state.set_state(Form.name)
    await state.update_data(language=chosen_language)

    if chosen_language == 'English':
        await message.answer(text= f'{LEXICON['English']}\n{message.from_user.first_name}{LEXICON['English1']}')
    elif chosen_language == 'Русский':
        await message.answer(text= f'{LEXICON['Русский']}\n{message.from_user.first_name}{LEXICON['Русский1']}')
