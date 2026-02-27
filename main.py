import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from bot.handlers import common, crypto

async def main():
    # Логтарды қосу (қателерді көру үшін)
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Роутерлерді тіркеу (Тәртіп маңызды!)
    dp.include_router(common.router)
    dp.include_router(crypto.router)
    
    print("🚀 Бот жұмысқа дайын...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())