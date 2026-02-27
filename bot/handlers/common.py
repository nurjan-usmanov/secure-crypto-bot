from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.keyboards.main_kb import get_main_kb
from database import add_user, update_activity, get_full_stats

router = Router()


# /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name
    )

    update_activity(message.from_user.id)

    await state.clear()

    welcome_text = (
        f"👋 <b>Привет, {message.from_user.first_name}!</b>\n\n"
        "Я помогу тебе зашифровать любое сообщение.\n"
        "Выберите действие ниже 👇"
    )

    await message.answer(
        welcome_text,
        reply_markup=get_main_kb(),
        parse_mode="HTML"
    )


# Дисклеймер
@router.message(F.text == "⚖️ Дисклеймер")
async def show_disclaimer(message: types.Message):
    update_activity(message.from_user.id)

    disclaimer = (
        "⚖️ <b>Дисклеймер</b>\n\n"
        "🔐 Бот предназначен для защиты личной переписки.\n\n"
        "📌 Используя сервис, вы:\n"
        "• несёте полную ответственность за свои действия\n"
        "• обязуетесь не нарушать законодательство\n"
        "• не используете бот в противоправных целях\n\n"
        "🚫 Разработчик не отвечает за действия пользователей.\n"
        "⚙️ Сервис предоставляется «как есть».\n\n"
        "Если вы не согласны с условиями — прекратите использование бота."
    )

    await message.answer(disclaimer, parse_mode="HTML")


# ☕️ О проекте
@router.message(F.text == "☕️ О проекте")
async def show_about(message: types.Message):
    update_activity(message.from_user.id)

    total_users, active_24h, online_now, total_messages = get_full_stats()

    about_text = (
        "☕️ <b>О проекте</b>\n\n"
        "🔐 <b>Что это?</b>\n"
        "Telegram-бот для безопасного шифрования и расшифровки сообщений.\n\n"
        "👥 <b>Для кого?</b>\n"
        "• для личной конфиденциальной переписки\n"
        "• для команд и рабочих чатов\n"
        "• для тех, кто ценит приватность\n\n"
        "📊 <b>Статистика бота</b>\n"
        f"👤 Всего пользователей: <b>{total_users}</b>\n"
        f"🔥 Активных за 24ч: <b>{active_24h}</b>\n"
        f"🟢 Сейчас онлайн: <b>{online_now}</b>\n"
        f"💬 Всего обработано сообщений: <b>{total_messages}</b>\n\n"
        "📢 Открыты к сотрудничеству и размещению рекламы.\n"
        "💼 Проект доступен к продаже при заинтересованности."
    )

    await message.answer(about_text, parse_mode="HTML")