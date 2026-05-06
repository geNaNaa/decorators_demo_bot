from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import storage

router = Router()


# ─── ДЕКОРАТОР: @router.message(Command("delete")) ──────────────────
@router.message(Command("delete"))
async def cmd_delete(message: Message) -> None:
    habits =storage.get_habits(message.from_user.id)
    if not habits:
        await message.answer("Нечего удалять — привычек нет.")
        return

    builder = InlineKeyboardBuilder()
    for habit_id, habit in habits.items():
        builder.button(text=f"Удалить: {habit['name']}", callback_data=f"del:{habit_id}")
    builder.adjust(1)

    await message.answer("Выбери привычку для удаления:", reply_markup=builder.as_markup())


# ─── ДЕКОРАТОР: @router.callback_query(F.data.startswith("del:")) ───
# Тот же паттерн что и "done:" — magic filter по префиксу callback_data.
@router.callback_query(F.data.startswith("del:"))
async def delete_habit(callback: CallbackQuery) -> None:
    habit_id = callback.data.split(":", maxsplit=1)[1]
    success = storage.delete_habit(callback.from_user.id, habit_id)

    if success:
        await callback.answer("Удалено!")
        await callback.message.edit_text("Привычка удалена.")
    else:
        await callback.answer("Привычка не найдена")
