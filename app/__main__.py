import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import BOT_TOKEN
from app.middlewares import LoggingMiddleware
from app.handlers import commands, add_habit, list_habits, stats, delete_habit


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # ── Middleware ────────────────────────────────────────────────────
    # inner middleware — логирует обработанные события
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # TODO (задание): раскомментируй после реализации AllowedUsersMiddleware
    # from app.middlewares import AllowedUsersMiddleware
    # dp.update.outer_middleware(AllowedUsersMiddleware())

    # ── Роутеры ──────────────────────────────────────────────────────
    # Каждый роутер — отдельный файл со своими хэндлерами.
    # include_routers подключает их к диспетчеру.
    # Порядок важен: первым подключается commands (там /cancel),
    # чтобы /cancel перехватывался раньше FSM-хэндлеров.
    dp.include_routers(
        add_habit.router,  # /add, /cancel — первым, чтобы /cancel работал в FSM
        commands.router,  # /start, /help
        list_habits.router,  # /list
        stats.router,  # /stats
        delete_habit.router,  # /delete
    )

    logging.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    asyncio.run(main())
