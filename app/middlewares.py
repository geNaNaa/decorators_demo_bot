"""
Middleware — это «обёртки», которые выполняются вокруг каждого хэндлера.

В aiogram есть два типа middleware:
  - outer middleware  — выполняется ДО фильтров (dp.message.outer_middleware)
  - inner middleware  — выполняется ПОСЛЕ фильтров, но ДО хэндлера (dp.message.middleware)

Порядок вызовов:
  Update → outer middleware → фильтры → inner middleware → handler
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────
# LoggingMiddleware (inner middleware) — РЕАЛИЗОВАН
# ─────────────────────────────────────────────────────────────────────
# Регистрируется как inner middleware: dp.message.middleware(LoggingMiddleware())
# Это значит, что он сработает ПОСЛЕ фильтров — только для сообщений,
# которые прошли хотя бы один фильтр и будут обработаны хэндлером.


class LoggingMiddleware(BaseMiddleware):
    """Логирует каждое обработанное событие: кто, что."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        user_info = f"user={user.id}" if user else "user=?"
        logger.info("[%s] %s", user_info, event.__class__.__name__)

        result = await handler(event, data)

        logger.info("[%s] handler completed", user_info)
        return result


# ─────────────────────────────────────────────────────────────────────
# AllowedUsersMiddleware (outer middleware) — ЗАДАНИЕ ДЛЯ ТЕБЯ!
# ─────────────────────────────────────────────────────────────────────
# Задача: допиши этот middleware так, чтобы бот отвечал
# ТОЛЬКО пользователям из ALLOWED_USERS.
#
# Подсказки:
# 1. ALLOWED_USERS — frozenset[int], объяви как модульную константу
#    (парси из env ALLOWED_USER_IDS)
# 2. Получи пользователя:  user = data.get("event_from_user")
# 3. Если user и user.id в ALLOWED_USERS — вызови handler
# 4. Иначе — return None (бот молчит)
#
# Регистрация (в bot.py):
#   dp.update.outer_middleware(AllowedUsersMiddleware())
#
# Как протестировать: напиши боту с аккаунта, которого НЕТ
# в ALLOWED_USER_IDS — бот не должен отвечать.


from os import getenv


ALLOWED_USERS: frozenset[int] = frozenset(
    [int(i.strip()) for i in getenv("ALLOWED_USER_IDS", "").split(",")]
)


class AllowedUsersMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:

        user = data.get("event_from_user")
        if user and user.id in ALLOWED_USERS:
            return await handler(event, data)
        else:
            logger.info("Юзер непонятная чмоня %s", user.id if user else None)
            return
