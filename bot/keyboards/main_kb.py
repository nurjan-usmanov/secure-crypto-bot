from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_kb():
    kb = [
        [KeyboardButton(text="🔐 Шифровать"), KeyboardButton(text="🔓 Расшифровать")],
        [KeyboardButton(text="⚖️ Дисклеймер"), KeyboardButton(text="☕️ О проекте")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)