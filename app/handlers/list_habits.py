from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import storage

router = Router()


# ─── ДЕКОРАТОР: @router.message(Command("list")) ────────────────────
@router.message(Command("list"))
async def cmd_list(message: Message) -> None:
    habits = storage.get_habits(message.from_user.id)
    if not habits:
        await message.answer("У тебя пока нет привычек. Добавь через /add")
        return

    builder = InlineKeyboardBuilder()
    for habit_id, habit in habits.items():
        builder.button(text=f"Done: {habit['name']}", callback_data=f"done:{habit_id}")
    builder.adjust(1)  # по одной кнопке в ряд

    await message.answer("Нажми кнопку, чтобы отметить привычку:", reply_markup=builder.as_markup())


# ─── ДЕКОРАТОР: @router.callback_query(F.data.startswith("done:")) ──
# Magic filter F.data.startswith("done:") проверяет,
# что callback_data начинается с префикса "done:".
#
# Это паттерн для передачи ID через inline-кнопки:
#   callback_data="done:a1b2c3d4" → habit_id = "a1b2c3d4"
#
# Альтернатива — CallbackData (фабрика), но startswith проще для понимания.
@router.callback_query(F.data.startswith("done:"))
async def mark_done(callback: CallbackQuery) -> None:
    habit_id = callback.data.split(":", maxsplit=1)[1]
    success = storage.mark_done(callback.from_user.id, habit_id)

    if success:
        await callback.answer("Отмечено!")
    else:
        await callback.answer("Привычка не найдена")

    # Пересобираем клавиатуру, чтобы показать актуальное состояние
    habits = storage.get_habits(callback.from_user.id)
    if not habits:
        await callback.message.edit_text("Все привычки удалены.")
        return

    builder = InlineKeyboardBuilder()
    for hid, habit in habits.items():
        builder.button(text=f"Done: {habit['name']}", callback_data=f"done:{hid}")
    builder.adjust(1)

    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
