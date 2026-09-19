#!/usr/bin/env python3

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"
KIT = ROOT / "apps/macos/ClaudexorKit/Sources/ClaudexorKit"
STRINGS = APP / "Resources/ru.lproj/Localizable.strings"

T = {
    # Settings tabs
    "General": "Основные",
    "Routing": "Маршрутизация",
    "Harnesses": "Агенты",
    "Connections": "Подключения",
    "Budget": "Бюджет",
    "Secrets": "Секреты",
    "Appearance": "Внешний вид",

    # General
    "Engine status": "Состояние движка",
    "Connected": "Подключено",
    "Reconnect": "Переподключиться",
    "Refresh metadata": "Обновить данные",
    "Advanced & About": "Дополнительно и о приложении",
    "App": "Приложение",
    "Author": "Автор",
    "License": "Лицензия",
    "Version": "Версия",
    "Engine version": "Версия движка",
    "Engine sha": "SHA движка",
    "Engine": "Движок",
    "Repository": "Репозиторий",
    "Review protocol": "Протокол проверки",
    "Reviewer timeout": "Тайм-аут проверки",
    "Reviewer retries": "Повторы проверки",
    "Delivery protocol": "Протокол применения",
    "Public architecture": "Архитектура",

    # Routing
    "Agent & Routing": "Агент и маршрутизация",
    "Routing goal": "Цель маршрутизации",
    "Paid fallback": "Платный резерв",
    "Quality tiers": "Уровни качества",
    "Primary harness": "Основной агент",
    "Env inheritance": "Наследование окружения",
    "Auth route": "Маршрут авторизации",

    # Harnesses
    "Harness Doctor & Auth": "Диагностика и авторизация агентов",
    "Workspace Git": "Git рабочего пространства",
    "Available": "Доступен",
    "Control API": "Control API",
    "Installed": "Установлено",
    "Native session": "Нативная сессия",
    "Stored key": "Сохранённый ключ",
    "Isolated api smoke": "Изолированная проверка API",
    "Provider auth file": "Файл авторизации провайдера",
    "Readonly enforcement": "Ограничение только на чтение",
    "Setup": "Настроить",
    "Manage": "Управление",
    "Unavailable": "Недоступно",
    "Ok": "ОК",

    # Connections
    "SSH Connections": "SSH-подключения",
    "From config": "Из конфигурации",
    "Choose an alias": "Выберите алиас",
    "New host": "Новый хост",
    "No remote connections": "Нет удалённых подключений",

    # Budget
    "Unlimited paid budget": "Неограниченный платный бюджет",
    "Max USD per run": "Максимум USD на запуск",
    "Fresh": "Актуально",

    # Secrets
    "Secret backend": "Хранилище секретов",

    # Appearance
    "Theme": "Тема",
    "System": "Системная",
    "Light": "Светлая",
    "Dark": "Тёмная",

    # Main screen
    "No threads yet": "Чатов пока нет",
    "Choose project": "Выбрать проект",
    "Type a message to send": "Введите сообщение",

    # Runtime
    "Could not verify the selected engine runtime; continuing with the compatible running engine.":
        "Не удалось проверить выбранную версию движка; работа продолжается с совместимой запущенной версией.",
    "Could not verify the running engine build; continuing with its compatible protocol.":
        "Не удалось проверить сборку запущенного движка; работа продолжается через совместимый протокол.",

    # Harness status
    "Ready by doctor.": "Готов — проверка пройдена.",
    "Not ready: doctor degraded.": "Не готов: проверка выявила ограничения.",
    "Not ready: unavailable.": "Не готов: недоступен.",

    # Quota
    "Subscription": "Подписка",
    "API key": "API-ключ",
    "Local": "Локально",
}


def esc(v):
    return v.replace("\\", "\\\\").replace('"', '\\"')


def add_strings():
    existing = STRINGS.read_text() if STRINGS.exists() else ""

    lines = []
    for k, v in T.items():
        marker = f'"{esc(k)}" = '
        if marker not in existing:
            lines.append(f'"{esc(k)}" = "{esc(v)}";')

    if lines:
        with STRINGS.open("a") as f:
            f.write("\n/* pass 2 */\n")
            f.write("\n".join(lines))
            f.write("\n")


def patch(path: Path):
    s = path.read_text()
    old = s

    # Label("Title", systemImage: ...)
    s = re.sub(
        r'Label\("([^"\\]+)",\s*systemImage:',
        lambda m: f'Label(L10n.t("{esc(m.group(1))}"), systemImage:'
        if m.group(1) in T else m.group(0),
        s
    )

    # Toggle("Title", ...)
    s = re.sub(
        r'Toggle\(\s*"([^"\\]+)",',
        lambda m: f'Toggle(\n                    L10n.t("{esc(m.group(1))}"),'
        if m.group(1) in T else m.group(0),
        s
    )

    # ContentUnavailableView("Title", ...)
    s = re.sub(
        r'ContentUnavailableView\(\s*"([^"\\]+)",',
        lambda m: f'ContentUnavailableView(\n                    L10n.t("{esc(m.group(1))}"),'
        if m.group(1) in T else m.group(0),
        s
    )

    # settingsGroup("Title", ...)
    s = re.sub(
        r'settingsGroup\("([^"\\]+)",',
        lambda m: f'settingsGroup(L10n.t("{esc(m.group(1))}"),'
        if m.group(1) in T else m.group(0),
        s
    )

    # KeyValueRow(key: "Title",
    s = re.sub(
        r'KeyValueRow\(key:\s*"([^"\\]+)",',
        lambda m: f'KeyValueRow(key: L10n.t("{esc(m.group(1))}"),'
        if m.group(1) in T else m.group(0),
        s
    )

    # TextField("Title", ...)
    s = re.sub(
        r'TextField\(\s*"([^"\\]+)",',
        lambda m: f'TextField(\n                L10n.t("{esc(m.group(1))}"),'
        if m.group(1) in T else m.group(0),
        s
    )

    if s != old:
        path.write_text(s)
        return True
    return False


def patch_runtime_strings():
    files = [
        APP / "LocalDaemonReconciler.swift",
        APP / "AppModel+Harnesses.swift",
    ]

    changed = 0

    for path in files:
        if not path.exists():
            continue

        s = path.read_text()
        old = s

        for k in [
            "Could not verify the selected engine runtime; continuing with the compatible running engine.",
            "Could not verify the running engine build; continuing with its compatible protocol.",
            "Ready by doctor.",
            "Not ready: doctor degraded.",
            "Not ready: unavailable.",
        ]:
            s = s.replace(
                f'"{k}"',
                f'L10n.t("{esc(k)}")'
            )

        if s != old:
            path.write_text(s)
            changed += 1

    return changed


def main():
    add_strings()

    changed = 0
    for p in APP.rglob("*.swift"):
        if p.name == "L10n.swift":
            continue
        changed += int(patch(p))

    changed += patch_runtime_strings()

    print(f"Pass 2 complete. Changed files: {changed}")


if __name__ == "__main__":
    main()
