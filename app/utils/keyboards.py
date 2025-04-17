from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_reply_keyboard(post_id: int, bot_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Ответить 💬",
                    url=f"https://t.me/{bot_username}?start=reply_{post_id}"
                )
            ]
        ]
    )

def moderation_keyboard(post_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve:{post_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{post_id}")
            ]
        ]
    )

