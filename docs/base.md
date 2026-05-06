# Теория: декораторы и архитектура бота

## Что такое декоратор?

Декоратор — это функция, которая оборачивает другую функцию и добавляет ей поведение.

Простой пример на чистом Python — декоратор без аргументов:

```python
def log(func):
    def wrapper(*args, **kwargs):
        print(f"Вызов {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log
def say_hello(name):
    print(f"Привет, {name}!")

say_hello("Миша")
# Вызов say_hello
# Привет, Миша!
```

`@log` — это сахар для `say_hello = log(say_hello)`. Функция `say_hello` заменяется на `wrapper`, который сначала печатает лог, а потом вызывает оригинал.

---

## Декораторы в aiogram

В aiogram декораторы используются для **регистрации handler**. Ты говоришь фреймворку: «когда придёт событие X, вызови функцию Y».

```python
@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Привет!")
```

`@router.message(Command("start"))` — декоратор с аргументом. Он регистрирует `cmd_start` как обработчик сообщений с командой `/start`.

Без декоратора функция существует, но aiogram о ней не знает и никогда не вызовет.

---

## Как устроен бот — путь сообщения

Когда пользователь пишет боту, aiogram обрабатывает сообщение по цепочке:

```
Telegram
  │
  ▼
Dispatcher (dp)
  │
  ▼
Outer Middleware          ← AllowedUsersMiddleware (задание 1)
  │                         проверяет доступ ДО всего остального
  ▼
Router                    ← add_habit, commands, list_habits, stats, delete_habit
  │
  ▼
Фильтры                  ← Command("start"), F.data.startswith("done:"), FSM state...
  │                         каждый handler проверяется по порядку
  ▼
Inner Middleware          ← LoggingMiddleware
  │                         логирует только то, что прошло фильтры
  ▼
Handler                   ← async def cmd_start(message): ...
  │                         выполняет логику и отвечает пользователю
  ▼
Telegram
```

Ключевой момент: **фильтры в декораторе** определяют, какой handler получит сообщение. Без совпадения — aiogram пробует следующий handler.

---

## Типы декораторов в этом боте

### 1. Command handler — `@router.message(Command("..."))`

**Файлы:** `app/handlers/commands.py`, и все остальные handlers.

```python
@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    ...
```

`Command("start")` — встроенный **фильтр**. Проверяет, что текст сообщения начинается с `/start`. Если да — вызывается функция. Если нет — aiogram идёт дальше, ищет другой handler.

---

### 2. FSM StateFilter — `@router.message(SomeState.step)`

**Файл:** `app/handlers/add_habit.py`

```python
@router.message(AddHabitFSM.waiting_for_name)
async def habit_name_entered(message: Message, state: FSMContext) -> None:
    ...
```

Декоратор с **состоянием** вместо команды. Handler сработает только когда пользователь находится в состоянии `AddHabitFSM.waiting_for_name`. Подробнее про FSM — ниже.

---

### 3. Callback Query + Magic Filter — `@router.callback_query(F.data.startswith("..."))`

**Файлы:** `app/handlers/add_habit.py`, `app/handlers/list_habits.py`, `app/handlers/delete_habit.py`

```python
@router.callback_query(F.data.startswith("done:"))
async def mark_done(callback: CallbackQuery) -> None:
    habit_id = callback.data.split(":", maxsplit=1)[1]
    ...
```

Когда пользователь нажимает inline-кнопку, Telegram присылает `CallbackQuery` с полем `data` — строкой, которую мы задали при создании кнопки.

`F.data.startswith("done:")` — **magic filter**. `F` — объект aiogram для фильтров в функциональном стиле.

Можно комбинировать фильтры:

```python
@router.callback_query(F.data == "confirm_add", AddHabitFSM.confirm)
```

Handler сработает только если ОБА условия истинны.

---

### 4. Middleware — class-based обёртка

**Файл:** `app/middlewares.py`

```python
class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data) -> Any:
        # код ДО handler
        result = await handler(event, data)
        # код ПОСЛЕ handler
        return result
```

Middleware — **обёртка вокруг handler**. Два типа:
- **outer** (`dp.message.outer_middleware(...)`) — выполняется ДО фильтров
- **inner** (`dp.message.middleware(...)`) — выполняется ПОСЛЕ фильтров, но ДО handler

В боте `LoggingMiddleware` — inner (логирует только обработанные события).

---

## FSM — конечный автомат

FSM (Finite State Machine) позволяет боту вести **пошаговый диалог**. Каждый пользователь может находиться в своём состоянии независимо от других.

Пример: команда `/add` запускает диалог добавления привычки.

```
Пользователь               Бот                        Состояние
─────────────               ───                        ─────────
/add                   →    "Введи название:"          waiting_for_name
"Бегать"               →    "Добавить «Бегать»?"       confirm
  [Подтвердить]        →    "Привычка добавлена!"      (сброс)
  [Отмена]             →    "Добавление отменено."     (сброс)
/cancel (в любой момент) →  "Действие отменено."       (сброс)
```

Состояния объявляются в `app/states.py`:

```python
class AddHabitFSM(StatesGroup):
    waiting_for_name = State()   # ждём название
    confirm = State()            # ждём подтверждения кнопкой
```

Как это работает в коде:
1. `/add` → `await state.set_state(AddHabitFSM.waiting_for_name)` — переводим в состояние
2. Следующее сообщение ловится декоратором `@router.message(AddHabitFSM.waiting_for_name)`
3. После подтверждения — `await state.clear()` — сбрасываем состояние

Без FSM пришлось бы хранить "на каком шаге пользователь" вручную в базе.
