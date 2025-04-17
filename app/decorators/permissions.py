from functools import wraps
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User


def admin_only():
    def decorator(func):
        @wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            session: AsyncSession = kwargs.get("session") or kwargs.get("data", {}).get("session")

            # получить пользователя
            result = await session.execute(
                User.__table__.select().where(User.telegram_id == message.from_user.id)
            )
            user = result.first()
            
            if not user or user[0].role != "admin":
                await message.answer("⛔ У вас нет доступа к этой команде.")
                return
            return await func(message, *args, **kwargs)
        return wrapper
    return decorator
