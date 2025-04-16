import asyncio
from aiogram import Bot, Dispatcher
from app.bot import start_bot
from config import BOT_TOKEN
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
    await start_bot(bot, dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
