from config import ADMIN_ID, CHANNEL_ID
from aiogram.types import Message
from aiogram import Bot
import uuid

# временное хранилище сообщений
message_queue = {}

async def save_message(message: Message):
    message_id = str(uuid.uuid4())[:8]
    message_queue[message_id] = message.text

    bot: Bot = message.bot
    if ADMIN_ID:
        await bot.send_message(
            ADMIN_ID,
            f"Новое сообщение для модерации:\n\n{message.text}\n\n"
            f"ID: <code>{message_id}</code>\n\n"
            f"Чтобы опубликовать, отправьте:\n/approve {message_id}"
        )

def get_queued_message(message_id: str):
    return message_queue.pop(message_id, None)
