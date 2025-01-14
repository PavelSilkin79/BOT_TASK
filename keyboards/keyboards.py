from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_RU
from lexicon.lexicon_en import LEXICON_EN


# Функция для генерации инлайн-клавиатур "на лету"
def create_inline_kb(width: int,
                     *args: str,
                     **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    en_ru_kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
                            # Проверяем наличие слова в обоих словарях
                text=LEXICON_RU.get(button) or LEXICON_EN.get(button) or button 
                buttons.append(InlineKeyboardButton(
                    text=text,
                    callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    en_ru_kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return en_ru_kb_builder.as_markup()

