from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID, CHANNEL_ID, GROUP_ID
from app.services.moderation import save_message, get_queued_message
from app.texts.messages import WELCOME_TEXT, WAIT_MODERATION_TEXT

router = Router()

@router.message(F.text == "/start")
async def start(message: Message):
    await message.answer(WELCOME_TEXT)
    if ADMIN_ID == 0:
        await message.answer(f"Ваш chat_id: <code>{message.chat.id}</code>")

@router.message(F.text.startswith("/approve "))
async def approve(message: Message):
    if message.chat.id != ADMIN_ID:
        return  # Только админ может одобрять

    message_id = message.text.split(" ", 1)[-1]
    text = get_queued_message(message_id)
    if text:
        await message.bot.send_message(CHANNEL_ID, text)
        await message.answer("Сообщение опубликовано.")
    else:
        await message.answer("Сообщение не найдено или уже опубликовано.")

@router.message(F.text)
async def handle_text(message: Message):
    await save_message(message)
    await message.answer(WAIT_MODERATION_TEXT)

# FSM для ответа
class ReplyState(StatesGroup):
    waiting_for_post_id = State()
    waiting_for_reply_text = State()

# Старт — команда /ответить
@router.message(F.text == "/ответить")
async def start_reply(message: Message, state: FSMContext):
    await message.answer("Введите ID сообщения, на которое хотите ответить:")
    await state.set_state(ReplyState.waiting_for_post_id)

@router.message(ReplyState.waiting_for_post_id)
async def receive_post_id(message: Message, state: FSMContext):
    await state.update_data(post_id=message.text)
    await message.answer("Введите текст вашего ответа:")
    await state.set_state(ReplyState.waiting_for_reply_text)

@router.message(ReplyState.waiting_for_reply_text)
async def send_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    post_id = data.get("post_id")
    reply_text = message.text

    try:
        reply = await message.bot.send_message(
            chat_id=GROUP_ID,
            text=reply_text,
            reply_to_message_id=int(post_id)
        )
        await message.answer("Ответ отправлен.")
    except Exception as e:
        await message.answer(f"Не удалось отправить ответ: {str(e)}")

    await state.clear()
