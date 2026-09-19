#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"
STRINGS = APP / "Resources/ru.lproj/Localizable.strings"

T = {
    # Composer
    "Ask": "Вопрос",
    "Agent": "Агент",
    "Plan": "План",
    "Choose project": "Выбрать проект",
    "No project (Ask only)": "Без проекта (только вопросы)",
    "Browse This Mac…": "Выбрать на этом Mac…",
    "Type a message to send": "Введите сообщение",
    "Message…": "Сообщение…",
    "Send": "Отправить",

    # Workspace panel
    "No thread open": "Чат не открыт",
    "Open a thread to see its changes, artifacts, and evidence.":
        "Откройте чат, чтобы увидеть изменения, артефакты и результаты.",

    # Composer options
    "Harness pool — Best-of runs these; the primary answers in chat":
        "Пул агентов — режим «Лучший из вариантов» запускает их параллельно; основной агент отвечает в чате",
    "Auto — routes across all available harnesses.":
        "Авто — маршрутизация между всеми доступными агентами.",
    "Models — per harness for THIS turn":
        "Модели — отдельно для каждого агента на этот запуск",
    "Budget": "Бюджет",
    "Web": "Веб",
    "Effort": "Уровень рассуждения",
    "Auth route": "Маршрут авторизации",
    "Workspace": "Рабочее пространство",
    "Isolated workspace": "Изолированное рабочее пространство",
    "Thread default": "Настройка чата",

    # Attachments
    "No screenshot was attached because capture was cancelled or unavailable.":
        "Скриншот не прикреплён: захват был отменён или недоступен.",

    # Auth sheet
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
    "Manage": "Управление",
    "Recheck": "Проверить снова",
    "Setup": "Настроить",
}

def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')

existing = STRINGS.read_text()

with STRINGS.open("a") as f:
    f.write("\n/* pass 8 */\n")
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

# -----------------------------------------------------
# Project picker
# -----------------------------------------------------

changed += patch("DesignSystemComponents.swift", [
    (
        'Label("Browse This Mac…", systemImage: "folder.badge.plus")',
        'Label(L10n.t("Browse This Mac…"), systemImage: "folder.badge.plus")'
    ),
    (
        'Text("No project (Ask only)")',
        'Text(L10n.t("No project (Ask only)"))'
    ),
    (
        'Label("No project (Ask only)",',
        'Label(L10n.t("No project (Ask only)"),'
    ),
])


# -----------------------------------------------------
# RunMode labels — это источник Ask/Agent/Plan
# -----------------------------------------------------

changed += patch("DomainModels.swift", [
    ('case .ask: return "Ask"',
     'case .ask: return L10n.t("Ask")'),

    ('case .agent: return "Agent"',
     'case .agent: return L10n.t("Agent")'),

    ('case .plan: return "Plan"',
     'case .plan: return L10n.t("Plan")'),
])


# -----------------------------------------------------
# Composer
# -----------------------------------------------------

for name in [
    "ThreadsScreen.swift",
    "ThreadsScreen+Conversation.swift",
    "ComposerSubmission.swift",
    "ComposerChips.swift",
]:
    changed += patch(name, [
        ('"Choose project"', 'L10n.t("Choose project")'),
        ('"Type a message to send"', 'L10n.t("Type a message to send")'),
        ('"Message…"', 'L10n.t("Message…")'),
        ('"Send"', 'L10n.t("Send")'),
    ])


# -----------------------------------------------------
# Right workspace
# -----------------------------------------------------

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


# -----------------------------------------------------
# Composer options popover
# -----------------------------------------------------

changed += patch("ComposerOptionsPopover.swift", [
    (
        'OptionSection(title: "Harness pool — Best-of runs these; the primary answers in chat")',
        'OptionSection(title: L10n.t("Harness pool — Best-of runs these; the primary answers in chat"))'
    ),
    (
        'Text("Auto — routes across all available harnesses.")',
        'Text(L10n.t("Auto — routes across all available harnesses."))'
    ),
    (
        'Text("Models — per harness for THIS turn")',
        'Text(L10n.t("Models — per harness for THIS turn"))'
    ),
    (
        'Text("Budget")',
        'Text(L10n.t("Budget"))'
    ),
    (
        'Text("Web")',
        'Text(L10n.t("Web"))'
    ),
    (
        'Text("Effort")',
        'Text(L10n.t("Effort"))'
    ),
    (
        'Text("Auth route")',
        'Text(L10n.t("Auth route"))'
    ),
    (
        'Text("Workspace")',
        'Text(L10n.t("Workspace"))'
    ),
    (
        'Text("Isolated workspace")',
        'Text(L10n.t("Isolated workspace"))'
    ),
    (
        'Text("Thread default")',
        'Text(L10n.t("Thread default"))'
    ),
])


# -----------------------------------------------------
# Screenshot cancellation notice
# -----------------------------------------------------

changed += patch("ComposerAttachments.swift", [
    (
        'notices: ["No screenshot was attached because capture was cancelled or unavailable."]',
        'notices: [L10n.t("No screenshot was attached because capture was cancelled or unavailable.")]'
    ),
])


# -----------------------------------------------------
# Auth Sheet
# -----------------------------------------------------

for name in [
    "AuthSheet.swift",
    "AuthSheetHeader.swift",
    "AuthSheetAccountsPanel.swift",
    "AuthSheetNativeSetupPanel.swift",
]:
    changed += patch(name, [
        ('Text("Codex Auth")', 'Text(L10n.t("Codex Auth"))'),
        ('Text("Claude Auth")', 'Text(L10n.t("Claude Auth"))'),
        ('Text("Readiness")', 'Text(L10n.t("Readiness"))'),
        ('Text("Accounts")', 'Text(L10n.t("Accounts"))'),
        ('Button("Done")', 'Button(L10n.t("Done"))'),
        ('Text("Add another account")', 'Text(L10n.t("Add another account"))'),
        ('Button("Add & log in")', 'Button(L10n.t("Add & log in"))'),
        ('Text("API-key fallback")', 'Text(L10n.t("API-key fallback"))'),
        ('Button("Store Key")', 'Button(L10n.t("Store Key"))'),
        (
            'TextField("name (optional, e.g. Work)"',
            'TextField(L10n.t("name (optional, e.g. Work)")'
        ),
    ])


# -----------------------------------------------------
# Manage / Recheck / Setup in agent cards
# -----------------------------------------------------

for name in [
    "OpsScreens+Auth.swift",
    "OnboardingView.swift",
]:
    changed += patch(name, [
        (
            'presentation.available ? "Manage" : "Setup"',
            'presentation.available ? L10n.t("Manage") : L10n.t("Setup")'
        ),
        (
            'Label("Recheck", systemImage: "arrow.clockwise")',
            'Label(L10n.t("Recheck"), systemImage: "arrow.clockwise")'
        ),
    ])


print()
print(f"Pass 8 complete. Changed files: {changed}")
