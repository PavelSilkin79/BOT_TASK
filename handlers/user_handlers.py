import random

from aiogram import  Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon_ru import LEXICON_RU
from lexicon.lexicon_en import LEXICON_EN
from keyboards.keyboards import  create_inline_kb
#from keyboards.pagination_kb import create_pagination_keyboard
from database.database import users_db



router = Router()

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
@router.message(Command(commands='check_ru'))
async def process_subscription_check_command(message: Message, bot: Bot):
    chat_id =  '-1002143209588' 
    is_subscribed = await check_subscription(bot, message.from_user.id, chat_id)
    
    if is_subscribed:
        #await state.set_state(Form.subscription_check)
        # Устанавливаем состояние "subscription_check"
        #await state.update_data(subscription_check=True)
        await message.answer(text=LEXICON_RU['project'], reply_markup=create_inline_kb(3, 'get', 'get_and', 'connect_to'))
       # await message.answer('Вы подписанны на канал, можете получать контент!')
    else:
        await message.answer(text='❌ Условия не выполнены!Чтобы получить 50 $GRUM, подпишись на наш канал: @test', reply_markup=create_inline_kb(1, 'check_subscription_ru'))
         
       # markup = types.InlineKeyboardMarkup()
       # markup.add(types.InlineKeyboardButton('Подписаться',
       #                                       url='https://t.me/+j2z25tbzRF0zNjMy'))

        #await message.answer('Для получения контента необходимо подписаться на канал!',
        #                 reply_markup=markup)
        #await message.answer('После подписки напишите любое сообщение для проверки'


#Обработчик команды проверки подписки
@router.message(Command(commands='check_en'))
async def process_subscription_check_command(message: Message, bot: Bot):
    chat_id =  '-1002143209588' 
    is_subscribed = await check_subscription(bot, message.from_user.id, chat_id)
    
    if is_subscribed:
        #await state.set_state(Form.subscription_check)
        # Устанавливаем состояние "subscription_check"
        #await state.update_data(subscription_check=True)
        await message.answer(text=LEXICON_EN['project_en'], reply_markup=create_inline_kb(3, 'get_en', 'get_and_en', 'connect_to_en'))
       # await message.answer('Вы подписанны на канал, можете получать контент!')
    else:
        await message.answer(text='❌ Condition not met!To receive 50 $GRUM subscribe to our channel: @test', reply_markup=create_inline_kb(1, 'check_subscription_en'))
         
       # markup = types.InlineKeyboardMarkup()
       # markup.add(types.InlineKeyboardButton('Подписаться',
       #                                       url='https://t.me/+j2z25tbzRF0zNjMy'))

        #await message.answer('Для получения контента необходимо подписаться на канал!',
        #                 reply_markup=markup)
        #await message.answer('После подписки напишите любое сообщение для проверки'


#Обработчик инлайн кнопки 'connect_to_ru'
@router.callback_query(lambda callback_query: callback_query.data == 'connect_to')
async def handle_connect_to(callback_query: CallbackQuery):
    await callback_query.message.answer(text=LEXICON_RU['connect_to_ru'], reply_markup=create_inline_kb(2, 'connect', 'main_menu'))

#Обработчик инлайн кнопки 'connect_to_en'
@router.callback_query(lambda callback_query: callback_query.data == 'connect_to_en')
async def handle_connect_to(callback_query: CallbackQuery):
    await callback_query.message.answer(text=LEXICON_EN['connect_to_en'], reply_markup=create_inline_kb(2, 'connect_en', 'main_menu_en'))


# Обработчик инлайн кнопки 'connect_en'
@router.callback_query(lambda callback_query: callback_query.data == 'connect_en')
async def handle_connect(callback_query: CallbackQuery):

    await callback_query.message.answer(text=LEXICON_EN['connect_en_1'])
    await callback_query.message.answer(text=LEXICON_EN['connect_en_2'], reply_markup=create_inline_kb(1,'main_menu_en'))

# Обработчик инлайн кнопки 'connect_ru'
@router.callback_query(lambda callback_query: callback_query.data == 'connect')
async def handle_connect(callback_query: CallbackQuery):

    await callback_query.message.answer(text=LEXICON_RU['connect_ru_1'])
    await callback_query.message.answer(text=LEXICON_RU['connect_ru_2'], reply_markup=create_inline_kb(1,'main_menu'))


#Обработчик инлайн кнопки 'main_menu''
@router.callback_query(lambda callback_query: callback_query.data == 'main_menu')
async def handle_main_menu(callback_query: CallbackQuery):
    await callback_query.message.answer(text=LEXICON_RU['project'], reply_markup=create_inline_kb(3, 'get', 'get_and', 'connect_to'))

#Обработчик инлайн кнопки 'main_menu_en''
@router.callback_query(lambda callback_query: callback_query.data == 'main_menu_en')
async def handle_main_menu(callback_query: CallbackQuery):
    await callback_query.message.answer(text=LEXICON_EN['project_en'], reply_markup=create_inline_kb(3, 'get_en', 'get_and_en', 'connect_to_en'))











