from aiogram.fsm.state import State, StatesGroup


class AddHabitFSM(StatesGroup):
    """Состояния для сценария добавления привычки (/add)."""

    waiting_for_name = State()  # Ожидаем ввод названия
    confirm = State()  # Ожидаем нажатие кнопки подтверждения
