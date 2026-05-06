from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app import storage

router = Router()


# ─── ДЕКОРАТОР: @router.message(Command("stats")) ───────────────────
@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    habits = storage.get_habits(message.from_user.id)
    if not habits:
        await message.answer("У тебя пока нет привычек. Добавь через /add")
        return

    lines: list[str] = ["Статистика:\n"]
    for habit_id, habit in habits.items():
        streak, week = storage.get_stats(message.from_user.id, habit_id)
        lines.append(f"<b>{habit['name']}</b>")
        lines.append(f"  streak: {streak} дн. подряд")
        lines.append(f"  за неделю: {week}/7\n")

    await message.answer("\n".join(lines))
