#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"
STRINGS = APP / "Resources/ru.lproj/Localizable.strings"

translations = {
    # Settings / sections
    "General": "Основные",
    "Routing": "Маршрутизация",
    "Harnesses": "Агенты",
    "Connections": "Подключения",
    "Budget": "Бюджет",
    "Secrets": "Секреты",
    "Appearance": "Внешний вид",

    "Engine status": "Состояние движка",
    "Connected": "Подключено",
    "Advanced & About": "Дополнительно и о приложении",
    "Agent & Routing": "Агент и маршрутизация",
    "Routing goal": "Цель маршрутизации",
    "Paid fallback": "Платный резерв",
    "Quality tiers": "Уровни качества",
    "Primary harness": "Основной агент",
    "Env inheritance": "Наследование окружения",
    "Auth route": "Маршрут авторизации",

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

    "Ready by doctor.": "Готов — проверка пройдена.",
    "Not ready: doctor degraded.": "Не готов: проверка выявила ограничения.",
    "Not ready: unavailable.": "Не готов: недоступен.",
    "Unavailable": "Недоступно",
    "Ok": "ОК",

    # Main
    "No threads yet": "Чатов пока нет",
    "Choose project": "Выбрать проект",
    "Type a message to send": "Введите сообщение",

    # Connections
    "SSH Connections": "SSH-подключения",
    "From config": "Из конфигурации",
    "Choose an alias": "Выберите алиас",
    "New host": "Новый хост",
    "No remote connections": "Нет удалённых подключений",

    # Budget
    "Unlimited paid budget": "Неограниченный платный бюджет",
    "Max USD per run": "Максимум USD на запуск",

    # Secrets
    "Secret backend": "Хранилище секретов",

    # Appearance
    "Theme": "Тема",
    "System": "Системная",
    "Light": "Светлая",
    "Dark": "Тёмная",

    # Quota
    "Fresh": "Актуально",
    "Stale": "Устарело",
    "Unknown": "Неизвестно",
    "Quota unknown": "Квота неизвестна",
    "Quota exhausted": "Квота исчерпана",
    "Quota cooling down": "Квота восстанавливается",
    "Account quota exhausted": "Квота аккаунта исчерпана",
    "Account cooling down": "Аккаунт ожидает восстановления квоты",
    "Engine offline": "Движок не запущен",
    "Could not refresh quota": "Не удалось обновить квоту",

    # account
    "Next up": "Следующий",
    "Verified": "Подтверждён",
    "Not verified — log in": "Не подтверждён — выполните вход",
    "Manage": "Управление",
    "Log in": "Войти",
}

def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')

existing = STRINGS.read_text() if STRINGS.exists() else ""

with STRINGS.open("a") as f:
    f.write("\n/* pass 3 */\n")
    for k, v in translations.items():
        needle = f'"{esc(k)}" = '
        if needle not in existing:
            f.write(f'"{esc(k)}" = "{esc(v)}";\n')


def replace(path_name, replacements):
    path = APP / path_name

    if not path.exists():
        print("missing:", path)
        return 0

    s = path.read_text()
    old = s

    for a, b in replacements:
        s = s.replace(a, b)

    if s != old:
        path.write_text(s)
        print("patched:", path_name)
        return 1

    return 0


changed = 0

# ---------------------------------------------------------
# Settings — принудительно переводим вкладки и section titles
# ---------------------------------------------------------

changed += replace("OpsScreens.swift", [
    (
        'Label("General", systemImage: "gearshape")',
        'Label(L10n.t("General"), systemImage: "gearshape")'
    ),
    (
        'Label("Routing", systemImage: "point.3.connected.trianglepath.dotted")',
        'Label(L10n.t("Routing"), systemImage: "point.3.connected.trianglepath.dotted")'
    ),
    (
        'Label("Harnesses", systemImage: "cpu")',
        'Label(L10n.t("Harnesses"), systemImage: "cpu")'
    ),
    (
        'Label("Connections", systemImage: "network")',
        'Label(L10n.t("Connections"), systemImage: "network")'
    ),
    (
        'Label("Budget", systemImage: "dollarsign.circle")',
        'Label(L10n.t("Budget"), systemImage: "dollarsign.circle")'
    ),
    (
        'Label("Secrets", systemImage: "key")',
        'Label(L10n.t("Secrets"), systemImage: "key")'
    ),
    (
        'Label("Appearance", systemImage: "paintpalette")',
        'Label(L10n.t("Appearance"), systemImage: "paintpalette")'
    ),

    (
        'settingsGroup("Budget", "dollarsign.circle")',
        'settingsGroup(L10n.t("Budget"), "dollarsign.circle")'
    ),
    (
        'settingsGroup("Advanced & About", "info.circle")',
        'settingsGroup(L10n.t("Advanced & About"), "info.circle")'
    ),

    (
        '"Unlimited paid budget",',
        'L10n.t("Unlimited paid budget"),'
    ),
    (
        '"Max USD per run",',
        'L10n.t("Max USD per run"),'
    ),

    ('KeyValueRow(key: "App",', 'KeyValueRow(key: L10n.t("App"),'),
    ('KeyValueRow(key: "Author",', 'KeyValueRow(key: L10n.t("Author"),'),
    ('KeyValueRow(key: "License",', 'KeyValueRow(key: L10n.t("License"),'),
    ('KeyValueRow(key: "Version",', 'KeyValueRow(key: L10n.t("Version"),'),
    ('KeyValueRow(key: "Engine version",', 'KeyValueRow(key: L10n.t("Engine version"),'),
    ('KeyValueRow(key: "Engine sha",', 'KeyValueRow(key: L10n.t("Engine sha"),'),
    ('KeyValueRow(key: "Engine",', 'KeyValueRow(key: L10n.t("Engine"),'),
    ('KeyValueRow(key: "Review protocol",', 'KeyValueRow(key: L10n.t("Review protocol"),'),
    ('KeyValueRow(key: "Reviewer timeout",', 'KeyValueRow(key: L10n.t("Reviewer timeout"),'),
    ('KeyValueRow(key: "Reviewer retries",', 'KeyValueRow(key: L10n.t("Reviewer retries"),'),
    ('KeyValueRow(key: "Delivery protocol",', 'KeyValueRow(key: L10n.t("Delivery protocol"),'),
    ('KeyValueRow(key: "Public architecture",', 'KeyValueRow(key: L10n.t("Public architecture"),'),
])

# Добавляем недостающие ключи About
about = {
    "App": "Приложение",
    "Author": "Автор",
    "License": "Лицензия",
    "Version": "Версия",
    "Engine version": "Версия движка",
    "Engine sha": "SHA движка",
    "Engine": "Движок",
    "Review protocol": "Протокол проверки",
    "Reviewer timeout": "Тайм-аут проверки",
    "Reviewer retries": "Повторы проверки",
    "Delivery protocol": "Протокол применения",
    "Public architecture": "Архитектура",
}

current = STRINGS.read_text()
with STRINGS.open("a") as f:
    for k, v in about.items():
        if f'"{esc(k)}" = ' not in current:
            f.write(f'"{esc(k)}" = "{esc(v)}";\n')


# ---------------------------------------------------------
# Harness readiness
# ---------------------------------------------------------

changed += replace("AppModel+Harnesses.swift", [
    ('return "Ready by doctor."',
     'return L10n.t("Ready by doctor.")'),
    ('return "Not ready: doctor degraded."',
     'return L10n.t("Not ready: doctor degraded.")'),
    ('return "Not ready: unavailable."',
     'return L10n.t("Not ready: unavailable.")'),
])


changed += replace("HarnessReadinessCard.swift", [
    # Server-projected titles/details:
    ('title: row.title,',
     'title: L10n.t(row.title),'),

    ('AlignedRowDetail(0, row.detail!)',
     'AlignedRowDetail(0, L10n.t(row.detail!))'),

    ('Label(presentation.health.rawValue.capitalized,',
     'Label(L10n.t(presentation.health.rawValue.capitalized),'),

    ('title: "Workspace Git",',
     'title: L10n.t("Workspace Git"),'),

    ('status: "Available",',
     'status: L10n.t("Available"),'),
])


# ---------------------------------------------------------
# Empty Threads state
# ---------------------------------------------------------

changed += replace("ThreadsScreen.swift", [
    (
        'ContentUnavailableView(\n                    "No threads yet",',
        'ContentUnavailableView(\n                    L10n.t("No threads yet"),'
    ),
])


# ---------------------------------------------------------
# Runtime warning
# ---------------------------------------------------------

changed += replace("LocalDaemonReconciler.swift", [
    (
        'notice: "Could not verify the selected engine runtime; continuing with the compatible running engine."',
        'notice: L10n.t("Could not verify the selected engine runtime; continuing with the compatible running engine.")'
    ),
    (
        'notice: "Could not verify the running engine build; continuing with its compatible protocol."',
        'notice: L10n.t("Could not verify the running engine build; continuing with its compatible protocol.")'
    ),
])

runtime_strings = {
    "Could not verify the selected engine runtime; continuing with the compatible running engine.":
        "Не удалось проверить выбранную версию движка; работа продолжается с совместимой запущенной версией.",

    "Could not verify the running engine build; continuing with its compatible protocol.":
        "Не удалось проверить сборку запущенного движка; работа продолжается через совместимый протокол.",
}

current = STRINGS.read_text()
with STRINGS.open("a") as f:
    for k, v in runtime_strings.items():
        if f'"{esc(k)}" = ' not in current:
            f.write(f'"{esc(k)}" = "{esc(v)}";\n')


# ---------------------------------------------------------
# Quota
# ---------------------------------------------------------

quota = APP / "QuotaViews.swift"
s = quota.read_text()
old = s

# Localized date. Это сразу превращает Sep -> сент. и PM -> 24h.
s = s.replace(
    '.locale(Locale(identifier: "en_US_POSIX")))',
    '.locale(Locale(identifier: "ru_RU")))'
)

s = s.replace(
    'Text(group.freshness.capitalized)',
    'Text(L10n.t(group.freshness.capitalized))'
)

s = s.replace(
    'availability.state == "exhausted" ? "Account quota exhausted" : "Account cooling down"',
    'availability.state == "exhausted" ? L10n.t("Account quota exhausted") : L10n.t("Account cooling down")'
)

s = s.replace(
    'Label("Cooling down until \\(cooldown)", systemImage: "hourglass")',
    'Label("Ожидание восстановления до \\(cooldown)", systemImage: "hourglass")'
)

s = s.replace(
    'Text("Resets \\(reset)")',
    'Text("Сброс \\(reset)")'
)

s = s.replace(
    'Text("\\(source.source.replacingOccurrences(of: "_", with: " ")) · observed \\(formattedDate(source.observedAt) ?? source.observedAt)")',
    'Text("\\(source.source.replacingOccurrences(of: "_", with: " ")) · получено \\(formattedDate(source.observedAt) ?? source.observedAt)")'
)

s = s.replace(
    'return "\\(Int((ratio * 100).rounded()))% used"',
    'return "Использовано \\(Int((ratio * 100).rounded()))%"'
)

if s != old:
    quota.write_text(s)
    changed += 1
    print("patched: QuotaViews.swift")


# ---------------------------------------------------------
# Account compact quota
# ---------------------------------------------------------

changed += replace("AccountRowView.swift", [
    ('badges.append(AlignedRowBadge("Next up",',
     'badges.append(AlignedRowBadge(L10n.t("Next up"),'),

    ('let summary = row.verified ? "Verified" : "Not verified — log in"',
     'let summary = row.verified ? L10n.t("Verified") : L10n.t("Not verified — log in")'),

    ('var text = "Quota exhausted"',
     'var text = L10n.t("Quota exhausted")'),

    ('text += " · resets \\(reset)"',
     'text += " · сброс \\(reset)"'),

    ('var text = "Quota cooling down"',
     'var text = L10n.t("Quota cooling down")'),

    ('text += " · until \\(reset)"',
     'text += " · до \\(reset)"'),

    ('var text = "\\(pct)% used"',
     'var text = "Использовано \\(pct)%"'),

    ('return AlignedRowDetail(0, "Quota unknown",',
     'return AlignedRowDetail(0, L10n.t("Quota unknown"),'),

    ('Button(row.verified ? "Manage" : "Log in", action: login)',
     'Button(row.verified ? L10n.t("Manage") : L10n.t("Log in"), action: login)')
])


print()
print(f"Pass 3 complete. Changed files: {changed}")
