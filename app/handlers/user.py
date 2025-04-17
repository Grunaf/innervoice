from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID, CHANNEL_ID, GROUP_ID, BOT_USERNAME
from app.services.moderation import save_message
from app.texts.messages import WELCOME_TEXT, WAIT_MODERATION_TEXT
from app.utils.keyboards import get_reply_keyboard
from app.database.models import Post, Reply, User
from app.database.db import async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from decorators.permissions import admin_only
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("admin"))
@admin_only()
async def admin_panel(message: Message, **data):
    await message.answer("Добро пожаловать в админ-панель.")
    logger.info(f"Админ панель: {message.from_user.id}")


@router.message(Command("setrole"))
@admin_only()
async def set_role_command(message: Message, command: CommandObject, **data):
    session: AsyncSession = data["session"]

    args = command.args
    if not args:
        await message.answer("⚠️ Формат: /setrole @username роль")
        return

    try:
        username, new_role = args.split()
        username = username.lstrip("@").lower()
    except ValueError:
        await message.answer("⚠️ Формат: /setrole @username роль")
        return

    result = await session.execute(
        select(User).where(User.telegram_username.ilike(username))
    )
    user = result.scalar_one_or_none()

    if not user:
        await message.answer(f"❌ Пользователь с username @{username} не найден в базе.")
        return

    user.role = new_role
    session.add(user)
    await session.commit()

    await message.answer(f"✅ Роль пользователя @{username} изменена на {new_role}")


@router.message(CommandStart(deep_link=True))
async def handle_start(message: Message, state: FSMContext, command: CommandStart):
    logger.info(f"/start от {message.from_user.id} | args={command.args}")
    if command.args and command.args.startswith("reply_"):
        post_id = command.args.replace("reply_", "")
        await state.set_state(ReplyState.waiting_for_reply_text)
        await state.update_data(post_id=int(post_id))
        await message.answer("Напиши свой ответ на сообщение.")
    else:
        await state.clear()
        await message.answer(WELCOME_TEXT)
        if ADMIN_ID == 0:
            await message.answer(f"Ваш chat_id: <code>{message.chat.id}</code>")

@router.callback_query(F.data.startswith("approve:"))
async def approve_post(callback: CallbackQuery):
    post_id = int(callback.data.split(":")[1])
    post = await get_post_by_id(post_id)
    logger.info(f"Одобрение поста {post.id} модератором {callback.from_user.id}")

    if not post or post.status != "pending":
        await callback.message.edit_text("⚠ Сообщение не найдено или уже обработано.")
        return

    msg = await callback.bot.send_message(
        CHANNEL_ID,
        post.text,
        reply_markup=get_reply_keyboard(post_id, BOT_USERNAME)
    )

    async with async_session() as session:
        post.status = "approved"
        post.message_id_in_channel = msg.message_id
        session.add(post)
        await session.commit()

    await callback.message.edit_text("✅ Сообщение опубликовано.")
    await callback.answer()


@router.callback_query(F.data.startswith("reject:"))
async def reject_post(callback: CallbackQuery):
    post_id = int(callback.data.split(":")[1])
    post = await get_post_by_id(post_id)
    logger.info(f"Отклонение поста {post.id} модератором {callback.from_user.id}")

    if not post or post.status != "pending":
        await callback.message.edit_text("⚠ Уже обработано или не найдено.")
        return

    async with async_session() as session:
        post.status = "rejected"
        session.add(post)
        await session.commit()

    await callback.message.edit_text("❌ Сообщение отклонено.")
    await callback.answer()


@router.message(F.text)
async def handle_text(message: Message):
    text = message.text.strip()
    if not text:
        await message.answer("⚠️ Сообщение не может быть пустым.")
        return

    if len(text) < 5:
        await message.answer("⚠️ Сообщение слишком короткое. Напиши чуть подробнее.")
        return
    
    async with async_session() as session:
        result = await session.execute(
            select(Post).where(
                Post.text == text,
                Post.author_id == message.from_user.id
            )
        )
        duplicate = result.scalar_one_or_none()

        if duplicate:
            await message.answer("⚠️ Похожее сообщение уже отправлено. Пожалуйста, подожди модерацию.")
            return
        
    await save_message(message)
    logger.info(f"Создан новый пост от {message.from_user.id}")
    await message.answer(WAIT_MODERATION_TEXT)

# FSM для ответа
class ReplyState(StatesGroup):
    waiting_for_reply_text = State()
from app.services.moderation import get_post_by_id

@router.message(ReplyState.waiting_for_reply_text)
async def send_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get("post_id")
    reply_text = message.text.strip()
    if not reply_text:
        await message.answer("⚠️ Ответ не может быть пустым.")
        await state.clear()
        return

    if len(reply_text) < 3:
        await message.answer("⚠️ Ответ слишком короткий.")
        await state.clear()
        return


    post = await get_post_by_id(post_id)

    if not post or not post.message_id_in_group:
        await message.answer("Не удалось отправить ответ: пост не найден или ещё не появился в обсуждении.")
        await state.clear()
        return

    try:
        sent = await message.bot.send_message(
            chat_id=GROUP_ID,
            text=reply_text,
            reply_to_message_id=post.message_id_in_group
        )
        
        # Сохраняем ответ в базу данных
        async with async_session() as session:
            new_reply = Reply(
                text=reply_text,
                parent_post_id=post.id,
                author_id=message.from_user.id,
                message_id_in_group=sent.message_id
            )
            session.add(new_reply)
            await session.commit()
        logger.info(f"Ответ на пост {post.id} от {message.from_user.id}")

        await message.answer("Ответ отправлен в обсуждение.")
    except Exception as e:
        await message.answer(f"Не удалось отправить ответ: {str(e)}")
        logger.exception(f"Ошибка при отправке ответа на пост {post_id}")


    await state.clear()



@router.message(F.chat.id == GROUP_ID)
async def handle_auto_post_in_group(message: Message):
    if message.forward_from_chat and message.forward_from_chat.id == CHANNEL_ID:
        original_message_id = message.forward_from_message_id

        # найти пост с таким message_id в канале
        async with async_session() as session:
            post = await session.execute(
                select(Post).where(Post.message_id_in_channel == original_message_id)
            )
            post = post.scalar_one_or_none()

            if post:
                post.message_id_in_group = message.message_id
                logger.info(f"Привязка поста {post.id} к сообщению в группе {message.message_id}")
                session.add(post)
                await session.commit()
