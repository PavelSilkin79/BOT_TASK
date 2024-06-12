from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon import LEXICON

# ------- Создаем клавиатуру через ReplyKeyboardBuilder -------

# Создаем кнопки с ответами согласия и отказа
en_button = KeyboardButton(text=LEXICON['en_button'])
ru_button = KeyboardButton(text=LEXICON['ru_button'])

# Инициализируем билдер для клавиатуры с кнопками "Давай" и "Не хочу!"
en_ru_kb_builder = ReplyKeyboardBuilder()

# Добавляем кнопки в билдер с аргументом width=2
en_ru_kb_builder.row(en_button, ru_button, width=2)

# Создаем клавиатуру с кнопками "Давай!" и "Не хочу!"
en_ru_kb: ReplyKeyboardMarkup = en_ru_kb_builder.as_markup(
    one_time_keyboard=True,
    resize_keyboard=True
)

# ------- Создаем игровую клавиатуру без использования билдера -------

# Создаем кнопки игровой клавиатуры
button_1 = KeyboardButton(text=LEXICON['rock'])
button_2 = KeyboardButton(text=LEXICON['scissors'])
button_3 = KeyboardButton(text=LEXICON['paper'])

# Создаем игровую клавиатуру с кнопками "Камень 🗿",
# "Ножницы ✂" и "Бумага 📜" как список списков
game_kb = ReplyKeyboardMarkup(
    keyboard=[[button_1],
              [button_2],
              [button_3]],
    resize_keyboard=True
)
language_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='English'), KeyboardButton(text='Русский')]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )