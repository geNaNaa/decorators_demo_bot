from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.states import AddHabitFSM
from app import storage

router = Router()


# ─── ДЕКОРАТОР: @router.message(Command("cancel")) ──────────────────
# Команда /cancel — сбрасывает FSM-состояние.
# StateFilter("*") не нужен: Command("cancel") сработает в любом состоянии,
# а state.clear() безопасно вызывать даже если состояния нет.
@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current is None:
        await message.answer("Нечего отменять.")
        return
    await state.clear()
    await message.answer("Действие отменено.")


# ─── ДЕКОРАТОР: @router.message(Command("add")) ─────────────────────
# Точка входа в FSM-сценарий: команда /add переводит пользователя
# в состояние AddHabitFSM.waiting_for_name.
# После этого СЛЕДУЮЩЕЕ сообщение пользователя попадёт
# в хэндлер с декоратором @router.message(AddHabitFSM.waiting_for_name).
@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext) -> None:
    await state.set_state(AddHabitFSM.waiting_for_name)
    await message.answer("Введи название привычки:")


# ─── ДЕКОРАТОР: @router.message(AddHabitFSM.waiting_for_name) ───────
# StateFilter — хэндлер сработает ТОЛЬКО когда пользователь
# находится в состоянии AddHabitFSM.waiting_for_name.
#
# Это ключевой механизм FSM (Finite State Machine):
# бот «помнит», на каком шаге диалога находится каждый пользователь.
# Пока пользователь в этом состоянии, ЛЮБОЕ текстовое сообщение
# (не команда) попадёт сюда.
@router.message(AddHabitFSM.waiting_for_name)
async def habit_name_entered(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer("Отправь текстовое название привычки.")
        return

    await state.update_data(name=message.text)
    await state.set_state(AddHabitFSM.confirm)

    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить", callback_data="confirm_add")
    builder.button(text="Отмена", callback_data="cancel_add")
    builder.adjust(2)

    await message.answer(
        f'Добавить привычку "{message.text}"?',
        reply_markup=builder.as_markup(),
    )


# ─── ДЕКОРАТОР: @router.callback_query(...) ─────────────────────────
# Реагирует на нажатие inline-кнопки «Подтвердить».
#
# Здесь ДВА фильтра в одном декораторе:
#   1) F.data == "confirm_add"  — magic filter, проверяет callback_data кнопки
#   2) AddHabitFSM.confirm      — StateFilter, работает только в нужном состоянии
#
# Хэндлер вызовется только если ОБА фильтра вернут True.
@router.callback_query(F.data == "confirm_add", AddHabitFSM.confirm)
async def confirm_add(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    name = data["name"]
    storage.add_habit(callback.from_user.id, name)
    await state.clear()
    await callback.message.edit_text(f'Привычка "{name}" добавлена!')
    # callback.answer() убирает «часики» на кнопке
    await callback.answer()


# ─── ДЕКОРАТОР: @router.callback_query(F.data == "cancel_add", ...) ─
# Аналогичный паттерн — кнопка «Отмена».
@router.callback_query(F.data == "cancel_add", AddHabitFSM.confirm)
async def cancel_add(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("Добавление отменено.")
    await callback.answer()
