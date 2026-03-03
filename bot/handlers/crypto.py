# import io
# import uuid
# from datetime import datetime
# from aiogram import Router, types, F, Bot
# from aiogram.fsm.context import FSMContext
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from cryptography.fernet import InvalidToken

# from bot.states.crypto_states import CryptoStates
# from bot.utils.crypto import (
#     get_crypto_key, encrypt_data, decrypt_data, 
#     pack_file, unpack_file
# )
# from bot.keyboards.main_kb import get_main_kb

# router = Router()

# # Максимальный размер файла: 10 МБ
# MAX_FILE_SIZE = 10 * 1024 * 1024
# BOT_LINK = "@SafarGo_bot"  # Боттың юзернеймін осы жерге жазыңыз

# # 1. Выбор действия (Шифрование/Расшифрование)
# @router.message(F.text.in_(["🔐 Шифровать", "🔓 Расшифровать"]))
# async def process_choice(message: types.Message, state: FSMContext):
#     action = "encrypt" if "Шифровать" in message.text else "decrypt"
#     await state.update_data(action=action)
#     await message.answer(
#         "✍️ Отправьте текст или файл (фото, документ):\n\n"
#         "⚠️ Максимальный размер: 10 МБ", 
#         reply_markup=types.ReplyKeyboardRemove()
#     )
#     await state.set_state(CryptoStates.waiting_for_text)

# # 2. Получение данных и проверка размера
# @router.message(CryptoStates.waiting_for_text)
# async def process_content(message: types.Message, state: FSMContext):
#     def check_size(size: int):
#         return size <= MAX_FILE_SIZE

#     if message.text:
#         if len(message.text) > 4000:
#             await message.answer("❌ Текст слишком длинный. Отправьте его как файл.")
#             return
#         await state.update_data(user_text=message.text, content_type="text")

#     elif message.document:
#         if not check_size(message.document.file_size):
#             await message.answer("❌ Файл слишком большой! Лимит: 10 МБ.")
#             return
#         await state.update_data(
#             file_id=message.document.file_id, 
#             content_type="file", 
#             orig_name=message.document.file_name
#         )

#     elif message.photo:
#         photo = message.photo[-1]
#         if not check_size(photo.file_size):
#             await message.answer("❌ Фото слишком большое! Лимит: 10 МБ.")
#             return
#         await state.update_data(
#             file_id=photo.file_id, 
#             content_type="photo", 
#             orig_name="image.jpg"
#         )

#     else:
#         await message.answer("❌ Отправьте текст, фото или документ.")
#         return

#     await message.answer("🔑 Введите ваш 5-значный код (он будет удален для безопасности):")
#     await state.set_state(CryptoStates.waiting_for_key)

# # 3. Обработка кода и вывод результата
# @router.message(CryptoStates.waiting_for_key)
# async def process_key(message: types.Message, state: FSMContext, bot: Bot):
#     user_data = await state.get_data()
#     code = message.text.strip()
    
#     try:
#         await message.delete()
#     except: 
#         pass
    
#     status_msg = await message.answer("⏳ Обработка...")
#     key = get_crypto_key(code)
    
#     builder = InlineKeyboardBuilder().row(
#         types.InlineKeyboardButton(text="🗑 Удалить результат", callback_data="delete_msg")
#     )

#     try:
#         if user_data['content_type'] == "text":
#             if user_data['action'] == "encrypt":
#                 # Шифрование текста
#                 encrypted_bytes = encrypt_data(user_data['user_text'].encode(), key)
#                 res = encrypted_bytes.decode()
#                 # Бот сілтемесін қосу
#                 final_text = (
#                     f"🔒 **Зашифровано в {BOT_LINK}:**\n\n"
#                     f"`{res}`\n\n"
#                     f"💡 Чтобы расшифровать, отправьте этот текст боту {BOT_LINK}"
#                 )
#                 await message.answer(final_text, parse_mode="Markdown", reply_markup=builder.as_markup())
#             else:
#                 # Дешифрование текста
#                 # Егер мәтінде бот сілтемесі болса, тек шифрды бөліп алу (қосымша логика қажет болуы мүмкін)
#                 clean_text = user_data['user_text'].split('\n')[0] if "Зашифровано" in user_data['user_text'] else user_data['user_text']
#                 res = decrypt_data(clean_text.encode(), key).decode()
#                 await message.answer(f"🔓 **Расшифрованный текст:**\n\n{res}", reply_markup=builder.as_markup())
        
#         else:
#             file = await bot.get_file(user_data['file_id'])
#             file_io = await bot.download_file(file.file_path)
#             file_bytes = file_io.read()

#             if user_data['action'] == "encrypt":
#                 to_encrypt = pack_file(user_data.get('orig_name', 'file.dat'), file_bytes)
#                 encrypted_res = encrypt_data(to_encrypt, key)
                
#                 file_name = f"secure_{uuid.uuid4().hex[:6]}.crypt"
#                 output = types.BufferedInputFile(encrypted_res, filename=file_name)
                
#                 await message.answer_document(
#                     output, 
#                     caption=f"🔒 Файл зашифрован. Расшифровать можно здесь: {BOT_LINK}", 
#                     reply_markup=builder.as_markup()
#                 )
            
#             else:
#                 decrypted_res = decrypt_data(file_bytes, key)
#                 orig_name, orig_data = unpack_file(decrypted_res)
#                 output = types.BufferedInputFile(orig_data, filename=orig_name)
                
#                 if user_data['content_type'] == "photo":
#                     await message.answer_photo(
#                         output, 
#                         caption="🔓 Фото успешно восстановлено.", 
#                         reply_markup=builder.as_markup()
#                     )
#                 else:
#                     await message.answer_document(
#                         output, 
#                         caption=f"🔓 Файл восстановлен: `{orig_name}`", 
#                         parse_mode="Markdown",
#                         reply_markup=builder.as_markup()
#                     )

#     except InvalidToken:
#         await message.answer("❌ **Неверный код!** Не удалось расшифровать данные.")
#     except Exception as e:
#         await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
#     await status_msg.delete()
#     await state.clear()
#     await message.answer("Что сделаем дальше?", reply_markup=get_main_kb())

# @router.callback_query(F.data == "delete_msg")
# async def delete_message_handler(callback: types.CallbackQuery):
#     await callback.message.delete()
#     await callback.answer("Удалено")







import io
import uuid
from datetime import datetime
from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from cryptography.fernet import InvalidToken

from bot.states.crypto_states import CryptoStates
from bot.utils.crypto import (
    get_crypto_key, encrypt_data, decrypt_data, 
    pack_file, unpack_file
)
from bot.keyboards.main_kb import get_main_kb

router = Router()

# Максимальный размер файла: 10 МБ
MAX_FILE_SIZE = 10 * 1024 * 1024

# 1. Выбор действия (Шифрование/Расшифрование)
@router.message(F.text.in_(["🔐 Шифровать", "🔓 Расшифровать"]))
async def process_choice(message: types.Message, state: FSMContext):
    action = "encrypt" if "Шифровать" in message.text else "decrypt"
    await state.update_data(action=action)
    await message.answer(
        "✍️ **Отправьте текст или файл (фото, документ):**\n\n"
        "⚠️ Максимальный размер: 10 МБ", 
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(CryptoStates.waiting_for_text)

# 2. Получение данных и проверка размера
@router.message(CryptoStates.waiting_for_text)
async def process_content(message: types.Message, state: FSMContext):
    def check_size(size: int):
        return size <= MAX_FILE_SIZE

    if message.text:
        if len(message.text) > 4000:
            await message.answer("❌ Текст слишком длинный. Отправьте его как файл.")
            return
        await state.update_data(user_text=message.text, content_type="text")

    elif message.document:
        if not check_size(message.document.file_size):
            await message.answer("❌ Файл слишком большой! Лимит: 10 МБ.")
            return
        await state.update_data(
            file_id=message.document.file_id, 
            content_type="file", 
            orig_name=message.document.file_name
        )

    elif message.photo:
        photo = message.photo[-1]
        if not check_size(photo.file_size):
            await message.answer("❌ Фото слишком большое! Лимит: 10 МБ.")
            return
        await state.update_data(
            file_id=photo.file_id, 
            content_type="photo", 
            orig_name="image.jpg"
        )

    else:
        await message.answer("❌ Отправьте текст, фото или документ.")
        return

    await message.answer("🔑 **Введите ваш 5-значный код:**\n(Сообщение будет удалено сразу после ввода)")
    await state.set_state(CryptoStates.waiting_for_key)

# 3. Обработка кода и вывод результата
@router.message(CryptoStates.waiting_for_key)
async def process_key(message: types.Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    code = message.text.strip()
    
    # Получаем ссылку на бота
    bot_info = await bot.get_me()
    bot_link = f"https://t.me/{bot_info.username}"
    
    try:
        await message.delete()
    except: 
        pass
    
    status_msg = await message.answer("⏳ Обработка данных...")
    key = get_crypto_key(code)
    
    builder = InlineKeyboardBuilder().row(
        types.InlineKeyboardButton(text="🗑 Удалить результат", callback_data="delete_msg")
    )

    try:
        if user_data['content_type'] == "text":
            if user_data['action'] == "encrypt":
                # Шифрование текста
                encrypted_bytes = encrypt_data(user_data['user_text'].encode(), key)
                res = encrypted_bytes.decode()
                
                final_text = (
                    f"🔒 Зашифрованный материал\n\n"
                    f"`{res}`\n\n"
                    f"🔓 Расшифровать можно через "
                    f"<a href=\"{bot_link}\">@SafarGo_bot</a>"
                )
                await message.answer(final_text, parse_mode="HTML", reply_markup=builder.as_markup())
            else:
                # Дешифрование текста
                # Таза шифрды алу (егер пайдаланушы боттың шаблонын толық жіберсе)
                raw_text = user_data['user_text']
                if "Зашифровано" in raw_text:
                    # Мәтін ішіндегі ` ` (backticks) арасындағы шифрды іздеу немесе жол бойынша бөлу
                    clean_text = raw_text.split('\n')[2] if len(raw_text.split('\n')) > 2 else raw_text
                else:
                    clean_text = raw_text
                
                res = decrypt_data(clean_text.strip().encode(), key).decode()
                await message.answer(f"🔓 **Расшифрованный текст:**\n\n{res}", reply_markup=builder.as_markup())
        
        else:
            file = await bot.get_file(user_data['file_id'])
            file_io = await bot.download_file(file.file_path)
            file_bytes = file_io.read()

            if user_data['action'] == "encrypt":
                to_encrypt = pack_file(user_data.get('orig_name', 'file.dat'), file_bytes)
                encrypted_res = encrypt_data(to_encrypt, key)
                
                file_name = f"secure_{uuid.uuid4().hex[:6]}.crypt"
                output = types.BufferedInputFile(encrypted_res, filename=file_name)
                
                await message.answer_document(
                    output, 
                    caption=f"🔒 Файл зашифрован.\nРасшифровать можно здесь: {bot_link}", 
                    reply_markup=builder.as_markup()
                )
            
            else:
                decrypted_res = decrypt_data(file_bytes, key)
                orig_name, orig_data = unpack_file(decrypted_res)
                output = types.BufferedInputFile(orig_data, filename=orig_name)
                
                if user_data['content_type'] == "photo":
                    await message.answer_photo(
                        output, 
                        caption="🔓 Фото успешно восстановлено.", 
                        reply_markup=builder.as_markup()
                    )
                else:
                    await message.answer_document(
                        output, 
                        caption=f"🔓 Файл восстановлен: `{orig_name}`", 
                        parse_mode="Markdown",
                        reply_markup=builder.as_markup()
                    )

    except InvalidToken:
        await message.answer("❌ **Неверный код!** Не удалось расшифровать данные.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    
    await status_msg.delete()
    await state.clear()
    await message.answer("Что желаете сделать теперь?", reply_markup=get_main_kb())

@router.callback_query(F.data == "delete_msg")
async def delete_message_handler(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
        await callback.answer("Сообщение удалено")
    except:
        await callback.answer("Не удалось удалить сообщение", show_alert=True)