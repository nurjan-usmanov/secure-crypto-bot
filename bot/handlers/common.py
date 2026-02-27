from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards.main_kb import get_main_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    welcome_text = (
        f"👋 **Привет, {message.from_user.first_name}!**\n\n"
        "Я помогу тебе зашифровать любое сообщение.\n"
        "Выберите действие ниже 👇"
    )
    await message.answer(welcome_text, reply_markup=get_main_kb())

@router.message(F.text == "⚖️ Дисклеймер")
async def show_disclaimer(message: types.Message):
    disclaimer = "⚖️ **Отказ от ответственности**\n\nАвтор не несет ответственности за..."
    await message.answer(disclaimer)