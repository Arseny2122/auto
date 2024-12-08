from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


async def start_kb_if_user_exist():
    kb_list = [
        [KeyboardButton(text="Отзыв")],
        [KeyboardButton(text="Записаться на услугу"), KeyboardButton(text="Связаться")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True
    )
    return keyboard


async def start_kb_if_user_not_exist():
    kb_list = [[KeyboardButton(text="Заполнить данные")]]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True
    )
    return keyboard


async def inline_start():
    services = ["Мойка", "Тонировка", "Хим-чистка", "Установка доп. оборудования"]
    kb_list = [
        [KeyboardButton(text="Мойка")],
        [KeyboardButton(text="Тонировка")],
        [KeyboardButton(text="Хим-чистка")],
        [KeyboardButton(text="Установка доп. оборудования")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True
    )
    return keyboard
