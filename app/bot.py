from aiogram import Bot, Dispatcher
from app.handlers import user

async def start_bot(bot: Bot, dp: Dispatcher):
    dp.include_routers(user.router)
