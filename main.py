import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.bot import start_bot
from config import BOT_TOKEN
from app.middlewares.ensure_user import EnsureUserMiddleware, DbSessionMiddleware
from app.database.models import Base
from app.database.db import engine

async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы проверены/созданы")

async def main():
    await on_startup()
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    
    dp.message.middleware(DbSessionMiddleware())
    dp.message.middleware(EnsureUserMiddleware())

    dp.callback_query.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(EnsureUserMiddleware())

    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(EnsureUserMiddleware())


    await start_bot(bot, dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,  # или DEBUG для разработки
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    asyncio.run(main())
