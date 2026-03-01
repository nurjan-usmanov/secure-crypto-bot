from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.states.crypto_states import CryptoStates
from bot.utils.crypto import get_crypto_key, encrypt_text, decrypt_text
from bot.keyboards.main_kb import get_main_kb

router = Router()

# 1. Шифрлау немесе Расшифровка таңдау
@router.message(F.text.in_(["🔐 Шифровать", "🔓 Расшифровать"]))
async def process_choice(message: types.Message, state: FSMContext):
    action = "encrypt" if "Шифровать" in message.text else "decrypt"
    await state.update_data(action=action)
    
    await message.answer("✍️ Введите текст:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CryptoStates.waiting_for_text)

# 2. Мәтінді қабылдау
@router.message(CryptoStates.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    await state.update_data(user_text=message.text)
    await message.answer("🔑 Введите ваш 5-значный код:")
    await state.set_state(CryptoStates.waiting_for_key)

# 3. Кодты өңдеу және Нәтиже
@router.message(CryptoStates.waiting_for_key)
async def process_key(message: types.Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    action = user_data['action']
    content = user_data['user_text']
    code = message.text.strip()
    
    # --- 1-ші ТҮЗЕТУ: Пайдаланушының кодын өшіру ---
    try:
        await message.delete() # Жазған кодын өшіреміз
    except Exception:
        pass # Егер құқық жетпесе (жеке чатта бұл жұмыс істеуі тиіс)
    
    confirm_msg = await message.answer("✅ Код принят и обрабатывается...")
    
    key = get_crypto_key(code)
    bot_user = await bot.get_me()
    bot_link = f"https://t.me/{bot_user.username}"

    try:
        if action == "encrypt":
            result = encrypt_text(content, key)
            # --- 2-ші ТҮЗЕТУ: Шифрланған мәтін + сілтеме ---
            response_text = (
                f"🔒 **Зашифрованный текст:**\n\n`{result}`\n\n"
                f"--- --- ---\n"
                f"💡 [Для расшифровки нажмите здесь]({bot_link})"
            )
            await message.answer(response_text, parse_mode="Markdown")
        
        else:
            result = decrypt_text(content, key)
            # --- 3-ші ТҮЗЕТУ: Расшифровка + Удалить батырмасы ---
            builder = InlineKeyboardBuilder()
            builder.row(types.InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_msg"))
            
            await message.answer(
                f"🔓 **Расшифрованный текст:**\n\n{result}",
                reply_markup=builder.as_markup()
            )
            
    except Exception:
        await message.answer("❌ Ошибка! Неверный код или поврежденные данные.")
    
    # Бастапқы хабарламаны өшіру (Код принят...)
    await confirm_msg.delete()
    
    await state.clear()
    await message.answer("Что дальше?", reply_markup=get_main_kb())

# 4. "Удалить" батырмасы үшін хэндлер
@router.callback_query(F.data == "delete_msg")
async def delete_message_handler(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer("Сообщение удалено")