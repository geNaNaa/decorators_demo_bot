from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


# ─── ДЕКОРАТОР: @router.message(Command("start")) ───────────────────
# Command("start") — встроенный фильтр aiogram.
# Проверяет, что текст сообщения начинается с /start.
# Когда пользователь отправляет /start, aiogram вызовет именно эту функцию.
@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот для трекинга привычек.\n\n"
        "Команды:\n"
        "/add — добавить привычку\n"
        "/list — список привычек (отметить выполнение)\n"
        "/stats — статистика\n"
        "/delete — удалить привычку\n"
        "/cancel — отменить текущее действие"
    )


# ─── ДЕКОРАТОР: @router.message(Command("help")) ────────────────────
# Тот же паттерн — другая команда, другая функция.
# Каждый декоратор @router.message(Command(...)) регистрирует
# свою функцию как обработчик конкретной команды.
@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Как пользоваться:\n\n"
        "1. /add — бот спросит название привычки, потом попросит подтвердить\n"
        "2. /list — покажет все привычки с кнопками для отметки\n"
        "3. /stats — streak (дней подряд) и статистика за неделю\n"
        "4. /delete — выбери привычку для удаления\n"
        "5. /cancel — отменить ввод на любом шаге"
    )
