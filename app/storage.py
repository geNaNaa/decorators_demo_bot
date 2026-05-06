"""
Хранилище привычек в JSON-файле.

Структура данных:
{
    "<user_id>": {
        "<habit_id>": {
            "name": "Зарядка",
            "created_at": "2026-03-01",
            "completions": ["2026-03-05", "2026-03-06"]
        }
    }
}
"""

import json
import uuid
from datetime import date, timedelta
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).parent / "habits.json"


def load_data() -> dict[str, Any]:
    if not DATA_FILE.exists():
        return {}
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_data(data: dict[str, Any]) -> None:
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def add_habit(user_id: int, name: str) -> str:
    data = load_data()
    uid = str(user_id)
    if uid not in data:
        data[uid] = {}
    habit_id = uuid.uuid4().hex[:8]
    data[uid][habit_id] = {
        "name": name,
        "created_at": date.today().isoformat(),
        "completions": [],
    }
    save_data(data)
    return habit_id


def get_habits(user_id: int) -> dict[str, Any]:
    data = load_data()
    return data.get(str(user_id), {})


def delete_habit(user_id: int, habit_id: str) -> bool:
    data = load_data()
    uid = str(user_id)
    if uid in data and habit_id in data[uid]:
        del data[uid][habit_id]
        save_data(data)
        return True
    return False


def mark_done(user_id: int, habit_id: str) -> bool:
    data = load_data()
    uid = str(user_id)
    if uid not in data or habit_id not in data[uid]:
        return False
    today = date.today().isoformat()
    completions: list[str] = data[uid][habit_id]["completions"]
    if today not in completions:
        completions.append(today)
        save_data(data)
    return True


def get_stats(user_id: int, habit_id: str) -> tuple[int, int]:
    """Возвращает (streak, done_this_week)."""
    data = load_data()
    uid = str(user_id)
    if uid not in data or habit_id not in data[uid]:
        return 0, 0

    completions = sorted(data[uid][habit_id]["completions"])
    if not completions:
        return 0, 0

    # streak — сколько дней подряд (включая сегодня) выполнялась привычка
    streak = 0
    check_date = date.today()
    completion_set = {c for c in completions}
    while check_date.isoformat() in completion_set:
        streak += 1
        check_date -= timedelta(days=1)

    # done_this_week — сколько раз за последние 7 дней
    week_ago = date.today() - timedelta(days=6)
    done_this_week = sum(1 for c in completions if c >= week_ago.isoformat())

    return streak, done_this_week
