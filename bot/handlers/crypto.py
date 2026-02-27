from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.crypto_states import CryptoStates
from bot.utils.crypto import get_crypto_key, encrypt_text, decrypt_text
from bot.keyboards.main_kb import get_main_kb

router = Router()

@router.message(F.text.in_(["🔐 Шифровать", "🔓 Расшифровать"]))
async def process_choice(message: types.Message, state: FSMContext):
    action = "encrypt" if "Шифровать" in message.text else "decrypt"
    await state.update_data(action=action)
    
    prompt = "✍️ Введите текст:"
    await message.answer(prompt, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CryptoStates.waiting_for_text)

@router.message(CryptoStates.waiting_for_text)
async def process_text(message: types.Message, state: FSMContext):
    await state.update_data(user_text=message.text)
    await message.answer("🔑 Введите ваш 5-значный код:")
    await state.set_state(CryptoStates.waiting_for_key)

@router.message(CryptoStates.waiting_for_key)
async def process_key(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    action = user_data['action']
    content = user_data['user_text']
    code = message.text.strip()
    
    key = get_crypto_key(code)

    try:
        if action == "encrypt":
            result = encrypt_text(content, key)
            await message.answer(f"🔒 **Результат:**\n\n`{result}`")
        else:
            result = decrypt_text(content, key)
            await message.answer(f"🔓 **Текст:**\n\n{result}")
    except Exception:
        await message.answer("❌ Ошибка! Неверный код.")
    
    await state.clear()
    await message.answer("Что дальше?", reply_markup=get_main_kb())