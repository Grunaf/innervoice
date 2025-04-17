from aiogram import BaseMiddleware
from app.database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def ensure_user_exists(user_id: int, session: AsyncSession, username: str | None = None):
    result = await session.execute(select(User).where(User.telegram_id == user_id))
    user = result.scalars().first()

    if not user:
        user = User(telegram_id=user_id, telegram_username=username)
        session.add(user)
    else:
        if user.telegram_username != username:
            user.telegram_username = username
            session.add(user)

    await session.commit()


class EnsureUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        session: AsyncSession = data["session"]
        user = getattr(event, "from_user", None)

        if user:
            await ensure_user_exists(user.id, session, user.telegram_username)

        return await handler(event, data)


