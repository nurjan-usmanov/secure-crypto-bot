import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from bot.handlers import common, crypto # Бұларды келесі қадамда жазамыз

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Хэндлерлерді тіркеу
    # dp.include_router(common.router)
    
    print("Бот іске қосылды...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())