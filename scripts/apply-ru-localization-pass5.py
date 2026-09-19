#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"
STRINGS = APP / "Resources/ru.lproj/Localizable.strings"


T = {
    # Routing
    "Routing goal": "Цель маршрутизации",
    "Paid fallback": "Платный резерв",
    "Primary harness": "Основной агент",
    "Env inheritance": "Наследование окружения",
    "Auth route": "Маршрут авторизации",
    "configured": "настроено",

    # Harness settings
    "Per-Harness Defaults": "Настройки агентов по умолчанию",
    "Model": "Модель",
    "Effort": "Уровень рассуждения",
    "Web": "Веб",
    "fallback model": "Резервная модель",
    "tools allow (comma-separated)": "Разрешённые инструменты (через запятую)",
    "tools deny (comma-separated)": "Запрещённые инструменты (через запятую)",

    "Setup": "Настроить",
    "Recheck": "Проверить снова",
    "Copy raw": "Копировать исходные данные",
    "Provider login": "Вход в провайдер",

    # Connections
    "SSH Connections": "SSH-подключения",
    "From config": "Из конфигурации",
    "Choose an alias": "Выберите алиас",
    "Add": "Добавить",
    "Rescan": "Пересканировать",
    "New host": "Новый хост",

    # Budget
    "Refresh": "Обновить",
    "Unknown": "Неизвестно",
    "Interactive questions": "Интерактивные вопросы",
    "Waiting policy": "Политика ожидания",
    "Positive whole minutes": "Количество минут",

    # Secrets
    "Trust — full project access": "Доверие — полный доступ к проекту",
    "Open Codex Auth": "Открыть авторизацию Codex",
    "Open Antigravity Auth": "Открыть авторизацию Antigravity",
    "Open Claude Auth": "Открыть авторизацию Claude",
    "Open Cursor Auth": "Открыть авторизацию Cursor",
    "Open OpenCode Auth": "Открыть авторизацию OpenCode",
    "Open Raw API Auth": "Открыть авторизацию Raw API",
    "Open OpenRouter Auth": "Открыть авторизацию OpenRouter",

    # Appearance
    "Theme": "Тема",
    "System": "Системная",
    "Light": "Светлая",
    "Dark": "Тёмная",
}


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def add_strings():
    existing = STRINGS.read_text()

    with STRINGS.open("a") as f:
        f.write("\n/* pass 5 */\n")
        for k, v in T.items():
            if f'"{esc(k)}" = ' not in existing:
                f.write(f'"{esc(k)}" = "{esc(v)}";\n')


def patch_file(filename, replacements):
    p = APP / filename
    if not p.exists():
        print("missing:", filename)
        return 0

    s = p.read_text()
    old = s

    for src, dst in replacements:
        s = s.replace(src, dst)

    if s != old:
        p.write_text(s)
        print("patched:", filename)
        return 1

    return 0


add_strings()
changed = 0


# ----------------------------------------------------
# ROUTING
# ----------------------------------------------------

changed += patch_file("SettingsScreen+GeneralSections.swift", [
    ('Picker(\n                    "Routing goal",',
     'Picker(\n                    L10n.t("Routing goal"),'),

    ('Picker(\n                    "Paid fallback",',
     'Picker(\n                    L10n.t("Paid fallback"),'),

    ('Picker("Primary harness",',
     'Picker(L10n.t("Primary harness"),'),

    ('Picker("Env inheritance",',
     'Picker(L10n.t("Env inheritance"),'),

    ('Picker("Auth route",',
     'Picker(L10n.t("Auth route"),'),

    ('Text("\\(qualityTierCount()) configured")',
     'Text("\\(qualityTierCount()) настроено")'),
])


# ----------------------------------------------------
# PER-HARNESS DEFAULTS
# ----------------------------------------------------

changed += patch_file("HarnessDefaultsRow.swift", [
    ('Picker(\n                        "Model",',
     'Picker(\n                        L10n.t("Model"),'),

    ('Picker(\n                        "Effort",',
     'Picker(\n                        L10n.t("Effort"),'),

    ('Picker("Web",',
     'Picker(L10n.t("Web"),'),

    ('TextField("fallback model",',
     'TextField(L10n.t("fallback model"),'),

    ('TextField("tools allow (comma-separated)",',
     'TextField(L10n.t("tools allow (comma-separated)"),'),

    ('TextField("tools deny (comma-separated)",',
     'TextField(L10n.t("tools deny (comma-separated)"),'),
])


# ----------------------------------------------------
# HARNESS SCREEN
# ----------------------------------------------------

changed += patch_file("SettingsScreen+GeneralSections.swift", [
    ('settingsGroup("Per-Harness Defaults",',
     'settingsGroup(L10n.t("Per-Harness Defaults"),'),
])

changed += patch_file("HarnessReadinessCard.swift", [
    ('Label("Copy raw", systemImage: "doc.on.doc")',
     'Label(L10n.t("Copy raw"), systemImage: "doc.on.doc")'),
])


# ----------------------------------------------------
# CONNECTIONS
# ----------------------------------------------------

changed += patch_file("RemoteConnectionSettingsViews.swift", [
    ('"SSH Connections"',
     'L10n.t("SSH Connections")'),

    ('Text("From config")',
     'Text(L10n.t("From config"))'),

    ('Text("New host")',
     'Text(L10n.t("New host"))'),

    ('"Choose an alias"',
     'L10n.t("Choose an alias")'),

    ('Button("Add")',
     'Button(L10n.t("Add"))'),

    ('Button("Rescan")',
     'Button(L10n.t("Rescan"))'),
])


# ----------------------------------------------------
# BUDGET / INTERACTIVE QUESTIONS
# ----------------------------------------------------

changed += patch_file("OpsScreens.swift", [
    ('settingsGroup("Interactive questions",',
     'settingsGroup(L10n.t("Interactive questions"),'),

    ('"Waiting policy",',
     'L10n.t("Waiting policy"),'),

    ('"Positive whole minutes",',
     'L10n.t("Positive whole minutes"),'),
])


# ----------------------------------------------------
# QUOTA
# ----------------------------------------------------

changed += patch_file("QuotaViews.swift", [
    ('Label("Refresh", systemImage: "arrow.clockwise")',
     'Label(L10n.t("Refresh"), systemImage: "arrow.clockwise")'),

    ('guard let ratio else { return "Unknown" }',
     'guard let ratio else { return L10n.t("Unknown") }'),
])


# Нормализация vendor quota labels.
p = APP / "QuotaViews.swift"
s = p.read_text()
old = s

needle = '''        case "30 day", "30 days", "30d", "month", "monthly":
            return "30 дней"
        default:
            return raw
'''

replacement = '''        case "30 day", "30 days", "30d", "month", "monthly":
            return "30 дней"
        case "1 reset credit available":
            return "Доступен 1 сброс лимита"
        case "reset credit available":
            return "Доступен сброс лимита"
        default:
            return raw
'''

if needle in s:
    s = s.replace(needle, replacement)

if s != old:
    p.write_text(s)
    print("patched quota vendor labels")


# ----------------------------------------------------
# SECRETS
# ----------------------------------------------------

changed += patch_file("SettingsScreen+GeneralSections.swift", [
    ('Button("Open Codex Auth")',
     'Button(L10n.t("Open Codex Auth"))'),

    ('Button("Open Antigravity Auth")',
     'Button(L10n.t("Open Antigravity Auth"))'),

    ('Button("Open Claude Auth")',
     'Button(L10n.t("Open Claude Auth"))'),

    ('Button("Open Cursor Auth")',
     'Button(L10n.t("Open Cursor Auth"))'),

    ('Button("Open OpenCode Auth")',
     'Button(L10n.t("Open OpenCode Auth"))'),

    ('Button("Open Raw API Auth")',
     'Button(L10n.t("Open Raw API Auth"))'),

    ('Button("Open OpenRouter Auth")',
     'Button(L10n.t("Open OpenRouter Auth"))'),
])


changed += patch_file("TrustSupport.swift", [
    ('SectionLabel("Trust — full project access",',
     'SectionLabel(L10n.t("Trust — full project access"),'),
])


# ----------------------------------------------------
# APPEARANCE
# ----------------------------------------------------

changed += patch_file("SettingsScreen+GeneralSections.swift", [
    ('Picker("Theme",',
     'Picker(L10n.t("Theme"),'),

    ('Text("System").tag',
     'Text(L10n.t("System")).tag'),

    ('Text("Light").tag',
     'Text(L10n.t("Light")).tag'),

    ('Text("Dark").tag',
     'Text(L10n.t("Dark")).tag'),
])


print()
print(f"Pass 5 complete. Changed files: {changed}")
