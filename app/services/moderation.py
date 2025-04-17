from config import ADMIN_ID
from aiogram.types import Message
from aiogram import Bot
from app.database.db import async_session
from app.utils.keyboards import moderation_keyboard
from app.database.models import Post


# временное хранилище сообщений
message_queue = {}



async def save_message(message: Message):
    bot: Bot = message.bot
    user_id = message.from_user.id
    text = message.text

    async with async_session() as session:
        new_post = Post(
            text=text,
            author_id=user_id,
            status="pending"
        )
        session.add(new_post)
        await session.commit()  # чтобы получить ID

        if ADMIN_ID:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"📝 Новое сообщение для модерации:\n\n"
                    f"{text}\n\n"
                    f"ID: <code>{new_post.id}</code>"
                ),
                reply_markup=moderation_keyboard(new_post.id)
            )

async def get_post_by_id(post_id: int):
    async with async_session() as session:
        post = await session.get(Post, post_id)
        return post

