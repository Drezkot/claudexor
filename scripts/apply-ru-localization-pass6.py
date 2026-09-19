#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"
STRINGS = APP / "Resources/ru.lproj/Localizable.strings"

T = {
    # Main chat
    "Ask": "Вопрос",
    "Choose project": "Выбрать проект",
    "Type a message to send": "Введите сообщение",
    "Send": "Отправить",
    "No thread open": "Чат не открыт",
    "Open a thread to see its changes, artifacts, and evidence.":
        "Откройте чат, чтобы увидеть его изменения, артефакты и результаты.",

    # Routing
    "Env inheritance": "Наследование окружения",
    "Auth route": "Маршрут авторизации",
    "configured": "настроено",

    # Harnesses
    "Per-Harness Defaults": "Настройки агентов по умолчанию",
    "Model": "Модель",
    "Effort": "Уровень рассуждения",
    "Setup": "Настроить",
    "Recheck": "Проверить снова",
    "Copy raw": "Копировать исходные данные",

    # Connections
    "Hosts come from ~/.ssh/config. Claudexor delegates keys, ssh-agent, known_hosts, MFA, ProxyJump, and ProxyCommand to /usr/bin/ssh.":
        "Хосты берутся из ~/.ssh/config. Claudexor передаёт ключи, ssh-agent, known_hosts, MFA, ProxyJump и ProxyCommand системному /usr/bin/ssh.",
    "From config": "Из конфигурации",
    "Choose an alias": "Выберите алиас",
    "Add": "Добавить",
    "Rescan": "Пересканировать",
    "New host": "Новый хост",
    "Create one here, or add a Host block to ~/.ssh/config yourself and press Rescan. Pattern hosts (wildcards) stay hidden — only concrete aliases can become connections.":
        "Создайте подключение здесь или добавьте блок Host в ~/.ssh/config и нажмите «Пересканировать». Шаблонные хосты с масками скрываются — подключениями могут стать только конкретные алиасы.",

    # Appearance
    "Theme": "Тема",
    "System": "Системная",
    "Light": "Светлая",
    "Dark": "Тёмная",

    # Budget
    "Interactive questions": "Интерактивные вопросы",
    "Waiting policy": "Политика ожидания",
    "Unknown": "Неизвестно",
}

def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')

existing = STRINGS.read_text()

with STRINGS.open("a") as f:
    f.write("\n/* pass 6 */\n")
    for k, v in T.items():
        if f'"{esc(k)}" = ' not in existing:
            f.write(f'"{esc(k)}" = "{esc(v)}";\n')

def patch(name, pairs):
    p = APP / name
    if not p.exists():
        print("missing:", name)
        return 0

    s = p.read_text()
    old = s

    for a, b in pairs:
        s = s.replace(a, b)

    if s != old:
        p.write_text(s)
        print("patched:", name)
        return 1

    return 0

changed = 0

# Main composer
changed += patch("ThreadsScreen.swift", [
    ('Text("Ask")', 'Text(L10n.t("Ask"))'),
    ('Text("Choose project")', 'Text(L10n.t("Choose project"))'),
    ('Text("Type a message to send")', 'Text(L10n.t("Type a message to send"))'),
    ('Button("Send")', 'Button(L10n.t("Send"))'),
])

# Right workspace empty state
changed += patch("ThreadWorkspacePanel.swift", [
    ('"No thread open"', 'L10n.t("No thread open")'),
    (
        'Text("Open a thread to see its changes, artifacts, and evidence.")',
        'Text(L10n.t("Open a thread to see its changes, artifacts, and evidence."))'
    ),
])

# Routing labels
changed += patch("SettingsScreen+GeneralSections.swift", [
    ('"Env inheritance"', 'L10n.t("Env inheritance")'),
    ('"Auth route"', 'L10n.t("Auth route")'),
    ('Text("\\(qualityTierCount()) configured")',
     'Text("\\(qualityTierCount()) настроено")'),
])

# Per harness header
changed += patch("SettingsScreen+GeneralSections.swift", [
    ('settingsGroup("Per-Harness Defaults",',
     'settingsGroup(L10n.t("Per-Harness Defaults"),'),
])

changed += patch("HarnessDefaultsRow.swift", [
    ('"Model",', 'L10n.t("Model"),'),
    ('"Effort",', 'L10n.t("Effort"),'),
])

# Connections
changed += patch("RemoteConnectionSettingsViews.swift", [
    (
        'Text("Hosts come from ~/.ssh/config. Claudexor delegates keys, ssh-agent, known_hosts, MFA, ProxyJump, and ProxyCommand to /usr/bin/ssh.")',
        'Text(L10n.t("Hosts come from ~/.ssh/config. Claudexor delegates keys, ssh-agent, known_hosts, MFA, ProxyJump, and ProxyCommand to /usr/bin/ssh."))'
    ),
    ('Text("From config")', 'Text(L10n.t("From config"))'),
    ('"Choose an alias"', 'L10n.t("Choose an alias")'),
    ('Button("Add")', 'Button(L10n.t("Add"))'),
    ('Button("Rescan")', 'Button(L10n.t("Rescan"))'),
    ('Text("New host")', 'Text(L10n.t("New host"))'),
    (
        'Text("Create one here, or add a Host block to ~/.ssh/config yourself and press Rescan. Pattern hosts (wildcards) stay hidden — only concrete aliases can become connections.")',
        'Text(L10n.t("Create one here, or add a Host block to ~/.ssh/config yourself and press Rescan. Pattern hosts (wildcards) stay hidden — only concrete aliases can become connections."))'
    ),
])

# Appearance
changed += patch("SettingsScreen+GeneralSections.swift", [
    ('Picker("Theme",', 'Picker(L10n.t("Theme"),'),
    ('Text("System").tag', 'Text(L10n.t("System")).tag'),
    ('Text("Light").tag', 'Text(L10n.t("Light")).tag'),
    ('Text("Dark").tag', 'Text(L10n.t("Dark")).tag'),
])

# Interactive questions
changed += patch("OpsScreens.swift", [
    ('settingsGroup("Interactive questions",',
     'settingsGroup(L10n.t("Interactive questions"),'),
    ('"Waiting policy",', 'L10n.t("Waiting policy"),'),
])

# quota Unknown
changed += patch("QuotaViews.swift", [
    ('return "Unknown"', 'return L10n.t("Unknown")'),
])

print()
print(f"Pass 6 complete. Changed files: {changed}")
