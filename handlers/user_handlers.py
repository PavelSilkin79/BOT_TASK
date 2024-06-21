import random

from aiogram import  Router, Bot
from config_data.config import Config, load_config
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon_ru import LEXICON_RU
from lexicon.lexicon_en import LEXICON_EN
from keyboards.keyboards import  create_inline_kb
from database.database import users_db



router = Router()

# Загружаем конфиг в переменную config
config: Config = load_config()

class Form(StatesGroup):
    id = State()
    name = State()
    user_answer = State()
    captcha_answer = State()
    language = State()
    user_data = State()
    subscription_check = State()
    
# ПРОВЕРКА подписки
async def check_subscription(bot: Bot, user_id: int, chat_id: str):
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator'] # проверяем что пользователь подписан
    except Exception as e:
        print(f'ошибка при проверки подписки: {e}')
        return False

# Этот хэндлер будет срабатывать на команду /start 
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.username

    # Добавляем данные пользователа в словпарь
    users_db[user_id] = {'user_name': user_name}

    await message.answer(text=LEXICON_RU['/start'])


# Этот хэндлер будет срабатывать на команду "/help"
# и отправлять пользователю сообщение со списком доступных команд в боте
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=f'{LEXICON_RU['/help']}')



# Этот хэндлер будет срабатывать на команду "/kapcha"
# и предлогать поьзователю решить капчу
@router.message(Command(commands='kapcha'))
async def process_continue_command(message: Message, state: FSMContext):
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    operation = random.choice(['+', '-'])
    answer = num1 + num2 if operation == '+' else num1 - num2

    # Сохраняем правильный ответ на капчу в данные пользователя
    await state.set_state(Form.captcha_answer)
    await state.update_data(captcha_answer=answer)
    question = f"What is {num1} {operation} {num2}?"

    await message.answer(text= f'{LEXICON_EN['capcha']}\n{question}')


    # Хендлер для проверки ответа на капчу
@router.message(lambda message: message.text.isdigit(), StateFilter(Form.captcha_answer))
async def check_captcha(message: Message, state: FSMContext):
    user_answer = int(message.text)
    user_data = await state.get_data()
    if user_answer == user_data.get('captcha_answer'):
        await message.answer(text='Выберите язык, \n Choose a language', reply_markup=create_inline_kb(2, 'en_button', 'ru_button'))
    else:
        await message.answer(text=LEXICON_RU['no'])


# Хендлер для выбора языка
@router.callback_query(lambda callback_query: callback_query.data in ['en_button', 'ru_button'], StateFilter(Form.captcha_answer))
async def choose_language(callback_query: CallbackQuery, state: FSMContext):
    chosen_language = callback_query.data 
    await state.update_data(language=chosen_language)
    if chosen_language == 'en_button':
        await callback_query.message.answer(text= f'{LEXICON_EN['English']} \n{callback_query.from_user.username}, {LEXICON_EN['English1']}')
    elif chosen_language == 'ru_button':
        await callback_query.message.answer(text= f'{LEXICON_RU['Русский']}\n{callback_query.from_user.username}{LEXICON_RU['Русский1']}')


#Обработчик команды проверки подписки
@router.message(Command(commands=['check_en', 'check_ru']))
async def process_subscription_check_command(message: Message, bot: Bot, state: FSMContext):
    # Определение языка
    lang = 'en' if message.text.startswith('/check_en') else 'ru'
    chat_id = config.tg_bot.chat_id 
    is_subscribed = await check_subscription(bot, message.from_user.id, chat_id)
    
    if is_subscribed:
        await state.set_state(Form.subscription_check)
        # Устанавливаем состояние "subscription_check"
        await state.update_data(subscription_check=True)
        # Создание текста и кнопок в зависимости от языка
        text=LEXICON_EN['project_en'] if lang == 'en' else LEXICON_RU['project']
        buttons = ['get_en', 'get_and_en', 'connect_to_en'] if lang == 'en' else ['get', 'get_and', 'connect_to']
        await message.answer(text=text, reply_markup=create_inline_kb(3, *buttons))
        # await message.answer('Вы подписанны на канал, можете получать контент!')
    else:
        text='❌ Condition not met!To receive 50 $GRUM subscribe to our channel: @test' if lang == 'en' else '❌ Условия не выполнены!Чтобы получить 50 $GRUM, подпишись на наш канал: @test'
        await message.answer(text=text, reply_markup=create_inline_kb(1, f'check_subscription_{lang}'))


#Обработчик инлайн кнопки 'connect_to_ru_en'
@router.callback_query(lambda callback_query: callback_query.data in ['connect_to', 'connect_to_en'])
async def handle_connect_to(callback_query: CallbackQuery):
    lang = 'en' if callback_query.data == 'connect_to_en' else 'ru'
    text = LEXICON_EN['connect_to_en_1'] if lang == 'en' else LEXICON_RU['connect_to_ru_1']
    buttons = ['connect_en', 'main_menu_en'] if lang =='en' else ['connect', 'main_menu']
    await callback_query.message.answer(text=text, reply_markup=create_inline_kb(2, *buttons))


# Обработчик инлайн кнопки 'connect_ru_en'
@router.callback_query(lambda callback_query: callback_query.data in ['connect_en', 'connect'])
async def handle_connect(callback_query: CallbackQuery):
    lang =  'en' if callback_query.data == 'connect_en' else 'ru'
    text = LEXICON_EN['connect_en_1'] if lang == 'en' else LEXICON_RU['connect_ru_1']
    buttons = ['en_1', 'en_2'] if lang =='en' else ['ru_1', 'ru_2']
    await callback_query.message.answer(text=text, reply_markup=create_inline_kb(2, *buttons))

# Обработчик инлайн кнопки 'connect_ru_en✅'
@router.callback_query(lambda callback_query: callback_query.data in ['en_1', 'ru_1'])
async def handle_connect(callback_query: CallbackQuery):
    lang =  'en' if callback_query.data == 'en_1' else 'ru'
    text = LEXICON_EN['connect_en_2'] if lang == 'en' else LEXICON_RU['connect_ru_2']
    buttons = ['main_menu_en'] if lang =='en' else ['main_menu']
    await callback_query.message.answer(text=text, reply_markup=create_inline_kb(1, *buttons)) 


# Обработчик инлайн кнопки 'connect_ru_en❌'
@router.callback_query(lambda callback_query: callback_query.data in ['en_2', 'ru_2'])
async def handle_connect(callback_query: CallbackQuery):
    lang =  'en' if callback_query.data == 'en_2' else 'ru'
    text = LEXICON_EN['connect_to_en_1'] if lang == 'en' else LEXICON_RU['connect_to_ru_1']
    buttons = ['connect_en', 'main_menu_en'] if lang =='en' else ['connect', 'main_menu']
    await callback_query.message.answer(text=text, reply_markup=create_inline_kb(2, *buttons)) 


#Обработчик инлайн кнопки 'main_menu''
@router.callback_query(lambda callback_query: callback_query.data in ['main_menu', 'main_menu_en'])
async def handle_main_menu(callback_query: CallbackQuery):
    lang = 'en'if callback_query.data == 'main_menu_en' else 'ru'
    text = LEXICON_EN['project_en'] if lang == 'en' else LEXICON_RU['project']
    buttons = ['get_en', 'get_and_en', 'connect_to_en'] if lang =='en' else ['get', 'get_and', 'connect_to']
    await callback_query.message.answer(text=text, reply_markup=create_inline_kb(3, *buttons))












