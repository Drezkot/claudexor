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
    "Message…": "Сообщение…",
    "No thread open": "Чат не открыт",
    "Open a thread to see its changes, artifacts, and evidence.":
        "Откройте чат, чтобы увидеть изменения, артефакты и результаты.",

    # General
    "Engine status": "Состояние движка",
    "Connected": "Подключено",
    "Repository": "Репозиторий",

    # Routing
    "configured": "настроено",

    # Harness actions
    "Manage": "Управление",
    "Setup": "Настроить",
    "Recheck": "Проверить снова",

    # Connections
    "SSH Connections": "SSH-подключения",
    "From config": "Из конфигурации",
    "New host": "Новый хост",
    "Add": "Добавить",
    "Rescan": "Пересканировать",
    "Choose an alias": "Выберите алиас",
    "No remote connections": "Нет удалённых подключений",
    "Hosts come from ~/.ssh/config. Claudexor delegates keys, ssh-agent, known_hosts, MFA, ProxyJump, and ProxyCommand to /usr/bin/ssh.":
        "Хосты берутся из ~/.ssh/config. Claudexor передаёт ключи, ssh-agent, known_hosts, MFA, ProxyJump и ProxyCommand системному /usr/bin/ssh.",
    "Create one here, or add a Host block to ~/.ssh/config yourself and press Rescan. Pattern hosts (wildcards) stay hidden — only concrete aliases can become connections.":
        "Создайте подключение здесь или добавьте блок Host в ~/.ssh/config и нажмите «Пересканировать». Шаблонные хосты с масками скрываются — подключениями могут стать только конкретные алиасы.",

    # Appearance
    "System": "Системная",
    "Light": "Светлая",
    "Dark": "Тёмная",

    # Accounts/Auth
    "Codex Auth": "Авторизация Codex",
    "Claude Auth": "Авторизация Claude",
    "Readiness": "Готовность",
    "Accounts": "Аккаунты",
    "Done": "Готово",
    "Add another account": "Добавить аккаунт",
    "Add & log in": "Добавить и войти",
    "API-key fallback": "Резервный API-ключ",
    "Store Key": "Сохранить ключ",
    "name (optional, e.g. Work)": "Название (необязательно, например Работа)",
}

def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')

existing = STRINGS.read_text()

with STRINGS.open("a") as f:
    f.write("\n/* pass 7 */\n")
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

# ------------------------------------------------
# MAIN CHAT
# ------------------------------------------------

changed += patch("ThreadWorkspacePanel.swift", [
    (
        'title: "No thread open",',
        'title: L10n.t("No thread open"),'
    ),
    (
        'message: "Open a thread to see its changes, artifacts, and evidence.",',
        'message: L10n.t("Open a thread to see its changes, artifacts, and evidence."),'
    ),
])

# В composer часть подписей может идти через вычисляемые label.
for name in [
    "ThreadsScreen.swift",
    "ComposerChips.swift",
    "ComposerSubmission.swift",
]:
    changed += patch(name, [
        ('Text("Ask")', 'Text(L10n.t("Ask"))'),
        ('Text("Choose project")', 'Text(L10n.t("Choose project"))'),
        ('Text("Type a message to send")', 'Text(L10n.t("Type a message to send"))'),
        ('Button("Send")', 'Button(L10n.t("Send"))'),
        ('TextField("Message…"', 'TextField(L10n.t("Message…")'),
    ])


# ------------------------------------------------
# GENERAL
# ------------------------------------------------

changed += patch("SettingsScreen+GeneralSections.swift", [
    ('Text("Engine status")', 'Text(L10n.t("Engine status"))'),
    ('Text("Connected")', 'Text(L10n.t("Connected"))'),
])

changed += patch("OpsScreens.swift", [
    ('aboutLinkRow("Repository",',
     'aboutLinkRow(L10n.t("Repository"),'),
])


# ------------------------------------------------
# ROUTING
# ------------------------------------------------

changed += patch("SettingsScreen+GeneralSections.swift", [
    ('Text("\\(qualityTierCount()) configured")',
     'Text("\\(qualityTierCount()) настроено")'),
])


# ------------------------------------------------
# HARNESS ACTIONS
# ------------------------------------------------

changed += patch("OpsScreens+Auth.swift", [
    (
        'presentation.available ? "Manage" : "Setup"',
        'presentation.available ? L10n.t("Manage") : L10n.t("Setup")'
    ),
    (
        'Label("Recheck", systemImage: "arrow.clockwise")',
        'Label(L10n.t("Recheck"), systemImage: "arrow.clockwise")'
    ),
])

changed += patch("OnboardingView.swift", [
    (
        'presentation.available ? "Manage" : "Setup"',
        'presentation.available ? L10n.t("Manage") : L10n.t("Setup")'
    ),
])


# ------------------------------------------------
# CONNECTIONS
# ------------------------------------------------

changed += patch("RemoteConnectionSettingsViews.swift", [
    (
        'SettingsGroup("SSH Connections", systemImage: "network")',
        'SettingsGroup(L10n.t("SSH Connections"), systemImage: "network")'
    ),
    (
        'Text(\n                    "Hosts come from ~/.ssh/config. Claudexor delegates keys, ssh-agent, known_hosts, MFA, ProxyJump, and ProxyCommand to /usr/bin/ssh.")',
        'Text(L10n.t("Hosts come from ~/.ssh/config. Claudexor delegates keys, ssh-agent, known_hosts, MFA, ProxyJump, and ProxyCommand to /usr/bin/ssh."))'
    ),
    (
        'OptionRow(label: "From config", labelWidth: 84)',
        'OptionRow(label: L10n.t("From config"), labelWidth: 84)'
    ),
    (
        'OptionRow(label: "New host", labelWidth: 84)',
        'OptionRow(label: L10n.t("New host"), labelWidth: 84)'
    ),
    (
        'Label("Add", systemImage: "plus")',
        'Label(L10n.t("Add"), systemImage: "plus")'
    ),
    (
        'Label("Rescan", systemImage: "arrow.clockwise")',
        'Label(L10n.t("Rescan"), systemImage: "arrow.clockwise")'
    ),
    (
        'Label("No remote connections", systemImage: "network.slash")',
        'Label(L10n.t("No remote connections"), systemImage: "network.slash")'
    ),
    (
        'Text(\n                        "Create one here, or add a Host block to ~/.ssh/config yourself and press Rescan. Pattern hosts (wildcards) stay hidden — only concrete aliases can become connections.")',
        'Text(L10n.t("Create one here, or add a Host block to ~/.ssh/config yourself and press Rescan. Pattern hosts (wildcards) stay hidden — only concrete aliases can become connections."))'
    ),
])


# ------------------------------------------------
# APPEARANCE
# ------------------------------------------------

changed += patch("SettingsScreen+GeneralSections.swift", [
    ('Text("System").tag', 'Text(L10n.t("System")).tag'),
    ('Text("Light").tag', 'Text(L10n.t("Light")).tag'),
    ('Text("Dark").tag', 'Text(L10n.t("Dark")).tag'),
])


# ------------------------------------------------
# AUTH SHEET
# ------------------------------------------------

for name in [
    "AuthSheet.swift",
    "AuthSheetHeader.swift",
    "AuthSheetAccountsPanel.swift",
    "AuthSheetNativeSetupPanel.swift",
]:
    changed += patch(name, [
        ('Text("Readiness")', 'Text(L10n.t("Readiness"))'),
        ('Text("Accounts")', 'Text(L10n.t("Accounts"))'),
        ('Button("Done")', 'Button(L10n.t("Done"))'),
        ('Text("Add another account")', 'Text(L10n.t("Add another account"))'),
        ('Button("Add & log in")', 'Button(L10n.t("Add & log in"))'),
        ('Text("API-key fallback")', 'Text(L10n.t("API-key fallback"))'),
        ('Button("Store Key")', 'Button(L10n.t("Store Key"))'),
        ('TextField("name (optional, e.g. Work)"',
         'TextField(L10n.t("name (optional, e.g. Work)")'),
    ])


print()
print(f"Pass 7 complete. Changed files: {changed}")
