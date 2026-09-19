#!/usr/bin/env python3

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

APP_ROOT = ROOT / "apps/macos/ClaudexorApp"
SRC = APP_ROOT / "Sources/ClaudexorApp"
RESOURCES = SRC / "Resources"
RU_DIR = RESOURCES / "ru.lproj"
STRINGS_FILE = RU_DIR / "Localizable.strings"
PACKAGE_FILE = APP_ROOT / "Package.swift"
L10N_FILE = SRC / "L10n.swift"
REPORT_FILE = ROOT / ".ru-localization-untranslated.txt"


TRANSLATIONS = {
    # Общие
    "Done": "Готово",
    "Cancel": "Отмена",
    "Retry": "Повторить",
    "Recheck": "Проверить снова",
    "Refresh": "Обновить",
    "Add": "Добавить",
    "Remove": "Удалить",
    "Open": "Открыть",
    "Close": "Закрыть",
    "Copy": "Копировать",
    "Install": "Установить",
    "Connect": "Подключиться",
    "Disconnect": "Отключиться",
    "Save name": "Сохранить имя",
    "Choose…": "Выбрать…",
    "Clear": "Очистить",
    "Default": "По умолчанию",
    "Auto": "Авто",
    "On": "Вкл.",
    "Off": "Выкл.",
    "None": "Нет",
    "Never": "Никогда",
    "Live": "Онлайн",
    "Cached": "Кэш",
    "Web": "Веб",
    "Ready": "Готово",
    "Editing…": "Редактирование…",
    "Saving…": "Сохранение…",
    "Saved": "Сохранено",
    "In progress": "Выполняется",

    # Аккаунты
    "Accounts": "Аккаунты",
    "Add another account": "Добавить аккаунт",
    "Sign in": "Войти",
    "Reload accounts": "Обновить аккаунты",
    "Remove from Claudexor": "Удалить из Claudexor",
    "Could not load accounts": "Не удалось загрузить аккаунты",
    "Could not refresh readiness and quota": "Не удалось обновить готовность и квоту",
    "Auto-switch accounts at quota limit": "Автоматически переключать аккаунты при достижении лимита",
    "Automatic (account pool)": "Автоматически (пул аккаунтов)",
    "name (optional, e.g. Work)": "Название (необязательно, например Работа)",

    # Квоты
    "Quota": "Квота",
    "Loading quota…": "Загрузка квоты…",
    "Provider did not report usage for this window.": "Провайдер не сообщил использование для этого периода.",
    "No official quota snapshot is available yet. Unknown is not shown as full headroom.":
        "Официальные данные о квоте пока недоступны. Неизвестное значение не считается свободным лимитом.",
    "Refreshing · last-known quota remains visible": "Обновление · последняя известная квота остаётся видимой",

    # Чаты / потоки
    "New Thread": "Новый чат",
    "Threads": "Чаты",
    "Start a thread": "Начать чат",
    "Send": "Отправить",
    "Starting…": "Запуск…",
    "Rename": "Переименовать",
    "Rename…": "Переименовать…",
    "Rename thread": "Переименовать чат",
    "Thread title": "Название чата",
    "Archive": "Архивировать",
    "Reopen": "Открыть снова",
    "More options": "Дополнительные параметры",
    "Thread workspace": "Рабочее пространство чата",
    "No threads yet": "Чатов пока нет",
    "Start a thread to work conversationally: plan, continue, race, review, apply — one conversation.":
        "Начните чат для работы в одном диалоге: планирование, продолжение, сравнение вариантов, проверка и применение.",
    "Type below to begin. Turns run in-place so the next turn sees the work — plan, then implement, in one conversation.":
        "Напишите сообщение ниже. Следующий шаг видит результаты предыдущего — можно сначала составить план, затем реализовать его в одном чате.",

    # Проекты / Composer
    "Choose project": "Выбрать проект",
    "No project (Ask only)": "Без проекта (только вопросы)",
    "Browse This Mac…": "Выбрать на этом Mac…",
    "Ask": "Вопрос",
    "Agent": "Агент",
    "Plan": "План",
    "Best-of": "Лучший из вариантов",
    "Pick a project to use Agent · Plan · Best-of": "Выберите проект для режимов Агент · План · Лучший из вариантов",
    "Delegate unavailable": "Делегирование недоступно",
    "Harness default": "Настройка агента по умолчанию",
    "Harness default only": "Только настройка агента",
    "Thread default": "Настройка чата",
    "primary": "основной",
    "default": "по умолчанию",

    # Модели
    "Couldn't load models": "Не удалось загрузить модели",
    "Loading models…": "Загрузка моделей…",
    "No routable harnesses for this intent.": "Нет доступных агентов для этой задачи.",
    "Loading model catalog…": "Загрузка каталога моделей…",
    "Model catalog unavailable": "Каталог моделей недоступен",
    "Model override": "Переопределение модели",

    # Авторизация
    "API key": "API-ключ",
    "API-key fallback": "Резервный API-ключ",
    "Native setup": "Нативная настройка",
    "Store Key": "Сохранить ключ",
    "Native login setup": "Настройка нативного входа",
    "Native harness auth first, API-key fallback when needed.":
        "В первую очередь используется нативная авторизация агента, API-ключ — только как резервный вариант.",
    "Open in browser": "Открыть в браузере",
    "Open private sign-in": "Открыть приватный вход",
    "Use browser sign-in instead": "Использовать вход через браузер",
    "Sign-in code": "Код входа",
    "Get a new link": "Получить новую ссылку",
    "Paste the code from the sign-in page:": "Вставьте код со страницы входа:",
    "Cancel Login": "Отменить вход",
    "Open Terminal sign-in": "Открыть вход через Terminal",
    "Reconnect": "Переподключиться",
    "Setup job": "Задача настройки",
    "Setup state": "Состояние настройки",
    "Guide": "Инструкция",

    # Настройки
    "Settings": "Настройки",
    "General": "Основные",
    "Appearance": "Внешний вид",
    "Harnesses": "Агенты",
    "Routing": "Маршрутизация",
    "Connections": "Подключения",
    "Secrets": "Секреты",
    "Budget": "Бюджет",
    "Primary harness": "Основной агент",
    "Mirror native": "Использовать нативную авторизацию",
    "Clean": "Чистый режим",
    "Quality": "Качество",
    "Economy": "Экономия",
    "When unavailable": "Если недоступно",
    "Allowed within cap": "Разрешено в пределах лимита",
    "Auto (subscription first)": "Авто (сначала подписка)",
    "Theme": "Тема",
    "Continue after timeout": "Продолжить после тайм-аута",
    "No automatic expiry": "Без автоматического истечения",

    # Review / delegation
    "Reviewers": "Проверяющие",
    "Approvals": "Разрешения",
    "Effort": "Уровень рассуждения",
    "An explicit panel enables review. Leave empty to use automatic reviewers when Review changes is on.":
        "Явно заданный список включает проверку. Оставьте пустым, чтобы использовать автоматических проверяющих.",
    "Delegated Claudexor run": "Делегированный запуск Claudexor",
    "Open parent run": "Открыть родительский запуск",
    "Council": "Совет агентов",
    "Candidates": "Кандидаты",
    "Cross-family review": "Перекрёстная проверка",

    # План
    "Answer required": "Требуется ответ",
    "Answers submitted": "Ответы отправлены",
    "The plan needs your answers": "Для плана нужны ваши ответы",
    "Wait for the running turn to finish": "Дождитесь завершения текущего шага",
    "pick one or more": "выберите один или несколько",
    "required": "обязательно",
    "submitted": "отправлено",

    # Вопросы
    "Needs your answer": "Нужен ваш ответ",
    "Or answer in your own words…": "Или ответьте своими словами…",
    "Send answer": "Отправить ответ",

    # Файлы / вложения
    "Files": "Файлы",
    "Images": "Изображения",
    "Images this run changed": "Изображения, изменённые этим запуском",
    "Attach files": "Прикрепить файлы",
    "Capture screen region": "Снимок области экрана",
    "Preparing attachments…": "Подготовка вложений…",
    "Remove attachment": "Удалить вложение",

    # Preview
    "Preview": "Предпросмотр",
    "Open preview": "Открыть предпросмотр",
    "Go": "Перейти",

    # Diff / изменения
    "Diff": "Изменения",
    "No file changes in this run yet.": "В этом запуске пока нет изменений файлов.",
    "No changes in this run.": "В этом запуске нет изменений.",
    "Changes will appear after the run captures its final patch.":
        "Изменения появятся после формирования итогового патча.",
    "Apply patch": "Применить патч",
    "Apply as branch": "Применить как ветку",
    "Applied to project": "Применено к проекту",
    "Applied": "Применено",
    "As branch": "Как ветка",
    "Open run": "Открыть запуск",
    "Run Again": "Запустить снова",
    "Run Again…": "Запустить снова…",
    "Copy Inspect Command": "Копировать команду проверки",
    "Copy Run ID": "Копировать ID запуска",
    "Copy Full Run ID": "Копировать полный ID запуска",
    "Copy Summary": "Копировать сводку",
    "Diagnostics summary": "Диагностическая сводка",
    "Artifacts": "Артефакты",
    "All artifact paths": "Все пути артефактов",
    "Access": "Доступ",
    "Choose access…": "Выбрать доступ…",
    "Isolated workspace": "Изолированное рабочее пространство",
    "Open in workspace": "Открыть в рабочем пространстве",

    # Решения / риск
    "Accept risk & unblock…": "Принять риск и разблокировать…",
    "Override & allow apply": "Переопределить и разрешить применение",
    "Override needs-human": "Переопределить требование участия человека",
    "Rerun with feedback…": "Перезапустить с замечаниями…",

    # Trust
    "Grant full access": "Разрешить полный доступ",
    "Trust — full project access": "Доверие — полный доступ к проекту",
    "No projects have full access.": "Нет проектов с полным доступом.",
    "Revoke": "Отозвать",
    "Not started": "Не запущено",

    # Remote / SSH
    "Remote": "Удалённо",
    "New SSH Host…": "Новый SSH-хост…",
    "New SSH Host": "Новый SSH-хост",
    "SSH host": "SSH-хост",
    "Remote path": "Удалённый путь",
    "Remote Harness Install": "Установка агента на удалённой машине",
    "Run installer": "Запустить установщик",
    "Install runtime…": "Установить среду…",
    "No remote connections": "Нет удалённых подключений",
    "Remove connection": "Удалить подключение",
    "Remove…": "Удалить…",
    "Rescan": "Пересканировать",
    "Saved projects": "Сохранённые проекты",
    "Nickname": "Название",
    "Choose Folder": "Выбрать папку",
    "Up": "Наверх",
    "Daemon log": "Журнал демона",
    "Dev server port": "Порт dev-сервера",
    "Copy Block": "Копировать блок",

    # Update
    "Update available": "Доступно обновление",
    "View release": "Открыть релиз",

    # Разное
    "About Claudexor": "О Claudexor",
    "Status": "Статус",
    "Copy raw": "Копировать исходные данные",
    "Copy message": "Копировать сообщение",
}



EXTRA_TRANSLATIONS = {
    "Applied to the project — this thread's worktree has been delivered.":
        "Применено к проекту — рабочая копия этого чата перенесена в основной проект.",

    "Approvals let this run change auto-protected gate/test paths; they never bypass the built-in critical/security path human gates.":
        "Разрешения позволяют этому запуску изменять автоматически защищённые пути проверок и тестов, но не обходят обязательное подтверждение для критических и связанных с безопасностью изменений.",

    "Claude": "Claude",
    "Cursor": "Cursor",
    "Codex (device code)": "Codex (код устройства)",

    "Claudexor does not broker SaaS OAuth. Every account is its own named row signed in through the official vendor CLI login; API-key refs are only the fallback route.":
        "Claudexor не выступает посредником OAuth для SaaS. Каждый аккаунт хранится отдельно и авторизуется через официальный CLI провайдера; API-ключ используется только как резервный способ.",

    "Claudexor mirrors native harness auth first, with API-key fallback through stored secret refs.":
        "Claudexor в первую очередь использует нативную авторизацию агента, а API-ключ — только как резервный вариант через сохранённый секрет.",

    "Claudexor removes this binding and any Claudexor-owned state or managed secret. A vendor credential for this OS user may be left unchanged.":
        "Claudexor удалит эту привязку, связанные с ней данные и управляемые секреты. Учётные данные провайдера для текущего пользователя macOS могут остаться без изменений.",

    "Claudexor requested a private browser session. Completing the sign-in in a window that is not signed into another account for this vendor reduces the risk of signing out other apps on this Mac — the vendor may still invalidate sibling sessions on its side.":
        "Claudexor запросил приватную сессию браузера. Выполнение входа в окне, где нет другого аккаунта этого провайдера, снижает риск выхода из других приложений на этом Mac. При этом сам провайдер всё равно может завершить связанные сессии.",

    "Codex is signed in and ready.":
        "Codex авторизован и готов к работе.",

    "Create & Add":
        "Создать и добавить",

    "degraded":
        "ограниченная готовность",

    "Engine-level defaults per harness: enable/disable, model override, effort, and web policy. Stored in ~/.claudexor/v3/config.yaml.":
        "Настройки каждого агента: включение, модель, уровень рассуждения и политика веб-доступа. Хранятся в ~/.claudexor/v3/config.yaml.",

    "Everything happens in one chat. Pick your project in the composer's project chip (the only place projects are selected); the composer opens in Agent for direct edits (Ask is the fallback with no project); switch to Best-of to run the harness pool against each other, or Plan to draft an approach you can then implement in the same thread.":
        "Вся работа происходит в одном чате. Выберите проект в панели сообщения; режим «Агент» позволяет напрямую изменять файлы, без проекта используется режим «Вопрос». «Лучший из вариантов» запускает нескольких агентов для сравнения результатов, а «План» сначала формирует подход, который затем можно реализовать в этом же чате.",

    "Granted before project paths were recorded — revoke with `claudexor trust --revoke-full-access` inside that repo.":
        "Разрешение было выдано до сохранения путей проекта. Отозвать его можно командой `claudexor trust --revoke-full-access` внутри репозитория.",

    "Harness Doctor":
        "Диагностика агента",

    "Keep Running":
        "Продолжить работу",

    "Loading settings from this engine…":
        "Загрузка настроек из текущего движка…",

    "New setup actions stay disabled until the daemon confirms whether a job is already active.":
        "Новые действия настройки будут недоступны, пока демон не подтвердит, выполняется ли уже другая задача.",

    "No plan yet — the agent posts its steps here as the run starts.":
        "Плана пока нет — агент добавит этапы сюда после начала выполнения.",

    "Open questions — answer on the plan turn in chat to continue.":
        "Есть открытые вопросы — ответьте на них в сообщении с планом, чтобы продолжить.",

    "Open this page in an isolated browser session, then enter the one-time code.":
        "Откройте эту страницу в изолированной сессии браузера и введите одноразовый код.",

    "Optional. Open a harness auth sheet to store fallback refs through the local secret store; raw values are never written into run params, jobs, patches, or summaries.":
        "Необязательно. Откройте окно авторизации агента, чтобы сохранить резервные данные через локальное хранилище секретов. Исходные значения никогда не записываются в параметры запусков, задачи, патчи или сводки.",

    "Projects allowed to run without a sandbox (access: full). Stored user-level in ~/.claudexor/v3/trust — never inside the repo, so versioned config can't self-grant it.":
        "Проекты, которым разрешена работа без песочницы (полный доступ). Разрешения хранятся на уровне пользователя в ~/.claudexor/v3/trust, а не в репозитории, поэтому конфигурация проекта не может самостоятельно выдать себе полный доступ.",

    "Secret values live in the v2 0600 file store. Run params and artifacts store refs/metadata only.":
        "Секретные значения хранятся в защищённом файловом хранилище с правами 0600. Параметры запусков и артефакты содержат только ссылки и метаданные.",

    "Set Up Claudexor":
        "Настроить Claudexor",

    "Setup stream lost after bounded reconnects. The job was not marked failed; reconnect to fetch its current server state.":
        "Соединение с процессом настройки потеряно после нескольких попыток переподключения. Задача не помечена как неудачная — подключитесь снова, чтобы получить её текущее состояние.",

    "Skip":
        "Пропустить",

    "Subscription":
        "Подписка",

    "The active setup state is unknown. A request may have reached the daemon even though its response was lost; reconnect before starting another job.":
        "Текущее состояние настройки неизвестно. Запрос мог дойти до демона, даже если ответ был потерян. Перед запуском новой задачи переподключитесь.",

    "The window is matte glass — the desktop shows faintly through it. Code and diffs stay on a solid surface for contrast. Reduce Transparency falls back to a solid backdrop.":
        "Окно использует эффект матового стекла, поэтому рабочий стол слегка просвечивает. Код и изменения отображаются на непрозрачном фоне для лучшей читаемости. При включённом «Уменьшении прозрачности» используется сплошной фон.",

    "This run needs a decision — decide from its card in the conversation.":
        "Для этого запуска требуется решение — выберите действие в его карточке в чате.",

    "This turn cannot be retried in place — send a new message instead.":
        "Этот шаг нельзя повторить на месте — отправьте новое сообщение.",

    "Turns are kept in a thread worktree — apply them to the project when ready.":
        "Изменения хранятся в отдельной рабочей копии чата — примените их к проекту, когда они будут готовы.",

    "Will append to ~/.ssh/config":
        "Будет добавлено в ~/.ssh/config",
}

TRANSLATIONS.update(EXTRA_TRANSLATIONS)



FINAL_STATIC_TRANSLATIONS = {
    "This codex build does not support in-app device-code sign-in. Use the Terminal sign-in instead.":
        "Эта версия Codex не поддерживает вход по коду устройства внутри приложения. Используйте вход через Terminal.",

    "This creates a new editable run. Exact Retry is the immutable replay action.":
        "Будет создан новый редактируемый запуск. «Точный повтор» воспроизводит исходный запуск без изменений.",

    "This records an auditable override bound to the current patch. Apply becomes available; a mutated patch invalidates the override.":
        "Будет сохранено проверяемое переопределение, привязанное к текущему патчу. После этого станет доступно применение изменений; изменение патча отменит переопределение.",

    "This run is no longer available.":
        "Этот запуск больше недоступен.",
}

TRANSLATIONS.update(FINAL_STATIC_TRANSLATIONS)


CALLS = [
    "Text",
    "Button",
    "Label",
    "TextField",
    "SecureField",
    "Picker",
    "Section",
]

# Только простой строковый literal без интерполяции.
CALL_RE = re.compile(
    r'\b(' + "|".join(CALLS) + r')\("([^"\\]*(?:\\.[^"\\]*)*)"\)'
)

MODIFIER_PATTERNS = [
    re.compile(r'\.navigationTitle\("([^"\\]*(?:\\.[^"\\]*)*)"\)'),
    re.compile(r'\.alert\("([^"\\]*(?:\\.[^"\\]*)*)"\)'),
]


def swift_unescape(value: str) -> str:
    # Нам нужны только самые безопасные escape.
    return (
        value
        .replace(r'\"', '"')
        .replace(r'\\', '\\')
    )


def swift_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', r'\"')


def strings_escape(value: str) -> str:
    return (
        value
        .replace("\\", "\\\\")
        .replace('"', r'\"')
        .replace("\n", r"\n")
    )


def ensure_package_localization():
    s = PACKAGE_FILE.read_text()

    if "defaultLocalization:" in s:
        return False

    needle = 'let package = Package(\n    name: "ClaudexorApp",\n'
    if needle not in s:
        raise RuntimeError("Не удалось автоматически обновить Package.swift")

    replacement = (
        'let package = Package(\n'
        '    name: "ClaudexorApp",\n'
        '    defaultLocalization: "en",\n'
    )

    PACKAGE_FILE.write_text(s.replace(needle, replacement, 1))
    return True


def ensure_l10n():
    expected = '''import Foundation
import SwiftUI

enum L10n {
    private static let russianBundle: Bundle = {
        guard
            let path = Bundle.module.path(forResource: "ru", ofType: "lproj"),
            let bundle = Bundle(path: path)
        else {
            print("[L10n] ru.lproj not found in Bundle.module")
            return Bundle.module
        }

        return bundle
    }()

    static func t(_ key: String) -> String {
        russianBundle.localizedString(
            forKey: key,
            value: key,
            table: "Localizable"
        )
    }
}
'''
    if L10N_FILE.exists() and L10N_FILE.read_text() == expected:
        return False

    L10N_FILE.write_text(expected)
    return True


def write_strings_file():
    RU_DIR.mkdir(parents=True, exist_ok=True)

    lines = [
        "/* Claudexor Russian localization — generated by scripts/apply-ru-localization.py */",
        "",
    ]

    for key in sorted(TRANSLATIONS, key=str.casefold):
        lines.append(
            f'"{strings_escape(key)}" = "{strings_escape(TRANSLATIONS[key])}";'
        )

    lines.append("")
    STRINGS_FILE.write_text("\n".join(lines))


def patch_swift_file(path: Path):
    original = path.read_text()
    text = original
    replaced = 0

    def call_replace(m):
        nonlocal replaced

        call = m.group(1)
        literal = m.group(2)
        key = swift_unescape(literal)

        # Никогда не трогаем динамические строки.
        if r"\(" in literal:
            return m.group(0)

        if key not in TRANSLATIONS:
            return m.group(0)

        replaced += 1
        return f'{call}(L10n.t("{swift_escape(key)}"))'

    text = CALL_RE.sub(call_replace, text)

    for pattern in MODIFIER_PATTERNS:
        def mod_replace(m, _pattern=pattern):
            nonlocal replaced

            literal = m.group(1)
            key = swift_unescape(literal)

            if r"\(" in literal or key not in TRANSLATIONS:
                return m.group(0)

            prefix = ".navigationTitle" if "navigationTitle" in m.group(0) else ".alert"
            replaced += 1
            return f'{prefix}(L10n.t("{swift_escape(key)}"))'

        text = pattern.sub(mod_replace, text)

    if text != original:
        path.write_text(text)

    return replaced


def collect_untranslated():
    found = {}

    for path in SRC.rglob("*.swift"):
        if path == L10N_FILE:
            continue

        text = path.read_text(errors="ignore")

        for m in CALL_RE.finditer(text):
            literal = m.group(2)

            if r"\(" in literal:
                continue

            key = swift_unescape(literal)

            # Уже обёрнутый L10n regex сюда обычно не попадёт.
            if key not in TRANSLATIONS:
                found.setdefault(key, set()).add(
                    str(path.relative_to(ROOT))
                )

        for pattern in MODIFIER_PATTERNS:
            for m in pattern.finditer(text):
                literal = m.group(1)
                if r"\(" in literal:
                    continue

                key = swift_unescape(literal)
                if key not in TRANSLATIONS:
                    found.setdefault(key, set()).add(
                        str(path.relative_to(ROOT))
                    )

    return found


def main():
    if not APP_ROOT.exists():
        print("ERROR: запускай скрипт из репозитория Claudexor.", file=sys.stderr)
        sys.exit(1)

    package_changed = ensure_package_localization()
    l10n_changed = ensure_l10n()
    write_strings_file()

    total_replaced = 0
    changed_files = 0

    for path in SRC.rglob("*.swift"):
        if path == L10N_FILE:
            continue

        count = patch_swift_file(path)

        if count:
            total_replaced += count
            changed_files += 1

    untranslated = collect_untranslated()

    report = []
    for key in sorted(untranslated, key=str.casefold):
        report.append(key)
        for path in sorted(untranslated[key]):
            report.append(f"    {path}")
        report.append("")

    REPORT_FILE.write_text("\n".join(report))

    print()
    print("=== Claudexor RU patch ===")
    print(f"Package.swift updated: {'yes' if package_changed else 'no'}")
    print(f"L10n.swift updated:    {'yes' if l10n_changed else 'no'}")
    print(f"Swift files changed:   {changed_files}")
    print(f"UI calls replaced:     {total_replaced}")
    print(f"Russian translations:  {len(TRANSLATIONS)}")
    print(f"Still untranslated:    {len(untranslated)}")
    print()
    print("Report:")
    print(REPORT_FILE)
    print()
    print("Next:")
    print("  cd apps/macos/ClaudexorApp")
    print("  swift build")
    print("  .build/arm64-apple-macosx/debug/ClaudexorApp")


if __name__ == "__main__":
    main()
