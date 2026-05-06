# Habit Tracker Bot — учебный проект про декораторы в aiogram 3

Телеграм-бот для трекинга привычек. Цель проекта — показать, как работают **декораторы** в aiogram 3.x на живом примере.

---

## Быстрый старт

### 1. Создай бота

Открой [@BotFather](https://t.me/BotFather) в Telegram:
- `/newbot` → придумай имя → получи токен вида `123456:ABC-DEF...`

### 2. Узнай свой Telegram ID

Открой [@userinfobot](https://t.me/userinfobot) — он пришлёт твой числовой ID.

### 3. Подготовь окружение (WSL2 / Ubuntu)

```bash
# Установи uv (менеджер пакетов для Python) — если ещё нет
curl -LsSf https://astral.sh/uv/install.sh | sh

# Перезапусти терминал или:
source ~/.bashrc
```

### 4. Распакуй и настрой

```bash
# Распакуй архив и перейди в папку
cd decorators_demo_bot

# uv сам скачает нужный Python и установит зависимости
uv sync

cp .env.example .env
# Открой .env и заполни:
#   BOT_TOKEN=<токен от BotFather>
#   ALLOWED_USER_IDS=<твой Telegram ID>
```

### 5. Запусти

```bash
uv run python -m app
```

Открой бота в Telegram → `/start`

---

## Команды бота

| Команда | Что делает |
|---------|-----------|
| `/start` | Приветствие и список команд |
| `/help` | Подробная справка |
| `/add` | Добавить новую привычку (FSM-диалог) |
| `/list` | Список привычек с кнопками "Done" |
| `/stats` | Streak и статистика за неделю |
| `/delete` | Удалить привычку |
| `/cancel` | Отменить текущий ввод |

---

## Структура проекта

```
decorators_demo_bot/
├── app/
│   ├── __init__.py
│   ├── __main__.py      # Точка входа: создание бота, подключение middleware и роутеров
│   ├── config.py        # Загрузка переменных окружения (BOT_TOKEN)
│   ├── states.py        # FSM-состояния (StatesGroup)
│   ├── storage.py       # Хранение привычек в JSON-файле
│   ├── middlewares.py   # LoggingMiddleware (реализован) + AllowedUsersMiddleware (задание)
│   └── handlers/
│       ├── commands.py      # /start, /help — Command handler
│       ├── add_habit.py     # /add, /cancel — FSM + callback_query
│       ├── list_habits.py   # /list — inline-кнопки + callback_query
│       ├── stats.py         # /stats
│       └── delete_habit.py  # /delete — inline-кнопки + callback_query
├── docs/
│   ├── base.md          # Теория: декораторы, FSM, архитектура
│   └── tasks.md         # Практические задания
└── .env.example
```

---

## Проверка кода

```bash
# Линтер — ловит стилистические ошибки и баги
uv run ruff check .

# Автоисправление того, что ruff умеет чинить сам
uv run ruff check --fix .

# Type checker — ловит ошибки типов
uv run basedpyright
```

> VS Code подсвечивает ошибки в открытых файлах автоматически (Ruff + basedpyright). Но `ruff check .` проверяет **все** файлы разом — удобно перед коммитом.

---

## Дальше

1. Прочитай [docs/base.md](docs/base.md) — теория про декораторы и архитектуру бота
2. Выполняй задания из [docs/tasks.md](docs/tasks.md)
