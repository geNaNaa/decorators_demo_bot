from aiogram.filters import BaseFilter
from aiogram.types import Message

from app import storage


class HasHabits(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        habits = storage.get_habits(message.from_user.id)
        return bool(habits)
