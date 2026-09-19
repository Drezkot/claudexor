#!/usr/bin/env python3

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"
STRINGS = APP / "Resources/ru.lproj/Localizable.strings"

TRANSLATIONS = {
    # Common
    "Cancel": "Отмена",
    "Retry": "Повторить",
    "Reconnect": "Переподключить",
    "Back": "Назад",
    "Ready": "Готово",
    "Settings": "Настройки",
    "Appearance": "Внешний вид",
    "New Thread": "Новый чат",
    "Thread workspace": "Рабочее пространство чата",
    "More options": "Дополнительные параметры",
    "Starting…": "Запуск…",
    "Saving…": "Сохранение…",
    "Saved": "Сохранено",

    # Composer
    "Attach files": "Прикрепить файлы",
    "Remove attachment": "Удалить вложение",
    "Capture screen region": "Снимок области экрана",
    "Model override": "Переопределение модели",
    "Delegate unavailable": "Делегирование недоступно",
    "Models — per harness for THIS turn": "Модели — отдельно для каждого агента на этот запуск",
    "Review controls": "Настройки проверки",
    "Workspace": "Рабочее пространство",
    "Agent strategy": "Стратегия агента",
    "Plan strategy": "Стратегия планирования",
    "Budget": "Бюджет",
    "Web": "Веб",
    "Effort": "Уровень рассуждения",
    "Auth route": "Маршрут авторизации",
    "Browser": "Браузер",
    "Test command": "Тестовая команда",
    "Thread default": "Настройка чата",
    "API key": "API-ключ",
    "Add": "Добавить",
    "Send answer": "Отправить ответ",
    "Or answer in your own words…": "Или напишите свой ответ…",

    # Auth
    "Accounts": "Аккаунты",
    "Done": "Готово",
    "Recheck": "Проверить снова",
    "Native setup": "Нативная настройка",
    "API-key fallback": "Резервный API-ключ",
    "Store Key": "Сохранить ключ",
    "Stay": "Остаться",
    "Open private sign-in": "Открыть приватный вход",
    "Open in browser": "Открыть в браузере",
    "Use browser sign-in instead": "Использовать вход через браузер",
    "Sign-in code": "Код входа",
    "Get a new link": "Получить новую ссылку",
    "Extend login wait (15 min)": "Продлить ожидание входа на 15 минут",
    "Cancel Login": "Отменить вход",
    "Setup job": "Задача настройки",
    "Open Terminal sign-in": "Открыть вход в Терминале",
    "Setup state": "Состояние настройки",

    # Accounts
    "Remove from Claudexor": "Удалить из Claudexor",
    "Sign in": "Войти",
    "Could not load accounts": "Не удалось загрузить аккаунты",
    "Could not refresh readiness and quota": "Не удалось обновить готовность и квоту",
    "name (optional, e.g. Work)": "Название (необязательно, например Работа)",
    "Scoped limits": "Ограничения модели",

    # Quota
    "Loading quota…": "Загрузка квоты…",
    "Refreshing · last-known quota remains visible": "Обновление · последняя известная квота остаётся видимой",
    "Engine offline": "Движок не подключён",

    # Workspace / evidence
    "Clear run filter": "Сбросить фильтр запуска",
    "Open preview": "Открыть предпросмотр",
    "No project output in this thread": "В этом чате пока нет результатов проекта",
    "Images this run changed": "Изображения, изменённые этим запуском",
    "Images": "Изображения",
    "Files": "Файлы",
    "Empty file": "Пустой файл",
    "(empty file)": "(пустой файл)",
    "Loading…": "Загрузка…",
    "Artifacts": "Артефакты",
    "Diagnostics summary": "Сводка диагностики",
    "Copy Run ID": "Копировать ID запуска",
    "Copy Inspect Command": "Копировать команду проверки",
    "Copy Summary": "Копировать сводку",
    "Run Again…": "Запустить снова…",
    "All artifact paths": "Все пути артефактов",
    "Access": "Доступ",
    "Run folder": "Папка запуска",
    "Diff": "Разница",
    "Thinking": "Размышление",

    # Delegation / review
    "Delegated Claudexor run": "Делегированный запуск Claudexor",
    "Open parent run": "Открыть родительский запуск",
    "No evidence — cannot block": "Нет доказательств — блокировка невозможна",
    "Override needs-human": "Переопределить требование участия человека",
    "Override & allow apply": "Переопределить и разрешить применение",
    "Accept risk & unblock": "Принять риск и разблокировать",
    "Rerun with feedback": "Перезапустить с обратной связью",

    # SSH
    "Choose…": "Выбрать…",
    "Identity file": "Файл идентификации",
    "Remove…": "Удалить…",
    "Remove connection": "Удалить подключение",
    "Copy Block": "Копировать блок",
    "Nickname": "Название",
    "SSH host": "SSH-хост",
    "Remote Harness Install": "Установка удалённого агента",
    "Codex device login": "Вход Codex по коду устройства",
    "Daemon log": "Лог демона",
    "Remote path": "Удалённый путь",
    "Dev server port": "Порт сервера разработки",

    # Misc
    "Copy message": "Копировать сообщение",
    "Revoke": "Отозвать",
    "Applied to project": "Применено к проекту",
    "Open in workspace": "Открыть в рабочем пространстве",
    "Answer required": "Требуется ответ",
    "Wait for the running turn to finish": "Дождитесь завершения текущего запуска",
}

def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')

# Add missing strings.
existing = STRINGS.read_text()
with STRINGS.open("a") as f:
    f.write("\n/* pass 10 */\n")
    for key, value in TRANSLATIONS.items():
        if f'"{esc(key)}" = ' not in existing:
            f.write(f'"{esc(key)}" = "{esc(value)}";\n')

# Constructors where replacing the literal with String is type-safe.
patterns = [
    (r'Text\("([^"]+)"\)', r'Text(L10n.t("\1"))'),
    (r'Button\("([^"]+)"', r'Button(L10n.t("\1")'),
    (r'Label\("([^"]+)",', r'Label(L10n.t("\1"),'),
    (r'TextField\("([^"]+)"', r'TextField(L10n.t("\1")'),
    (r'Picker\("([^"]+)"', r'Picker(L10n.t("\1")'),
    (r'SectionLabel\("([^"]+)",', r'SectionLabel(L10n.t("\1"),'),
    (r'OptionSection\(title:\s*"([^"]+)"\)', r'OptionSection(title: L10n.t("\1"))'),
    (r'OptionRow\(label:\s*"([^"]+)"', r'OptionRow(label: L10n.t("\1")'),
]

changed_files = 0
replaced = 0

for path in APP.rglob("*.swift"):
    if path.name in {"L10n.swift", "LocalizedPresentation.swift"}:
        continue

    text = path.read_text()
    old = text

    for pattern, replacement in patterns:
        def repl(m):
            global replaced
            key = m.group(1)

            # Only patch strings for which we explicitly own a translation.
            if key not in TRANSLATIONS:
                return m.group(0)

            replaced += 1
            return re.sub(pattern, replacement, m.group(0))

        text = re.sub(pattern, repl, text)

    if text != old:
        path.write_text(text)
        changed_files += 1
        print("patched:", path.relative_to(APP))

print()
print(f"Pass 10 complete. Changed files: {changed_files}")
print(f"UI calls replaced: {replaced}")
