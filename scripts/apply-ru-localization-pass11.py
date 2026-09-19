#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"
MAPPER = APP / "LocalizedPresentation.swift"

TRANSLATIONS = {
    # Engine / generic runtime
    "Engine offline.": "Движок не подключён.",
    "Engine offline": "Движок не подключён",
    "Request failed.": "Запрос не выполнен.",
    "Something went wrong. Try again.": "Произошла ошибка. Попробуйте ещё раз.",
    "Settings stopped loading.": "Загрузка настроек остановлена.",
    "Settings context changed while loading. Retry.": "Контекст настроек изменился во время загрузки. Повторите попытку.",
    "Engine offline — reconnect to load settings.": "Движок не подключён — переподключитесь для загрузки настроек.",
    "Engine offline — reconnect to check Git readiness.": "Движок не подключён — переподключитесь для проверки готовности Git.",
    "Engine offline: reconnect and try again.": "Движок не подключён — переподключитесь и попробуйте снова.",
    "Engine offline — reconnect to apply this thread.": "Движок не подключён — переподключитесь, чтобы применить изменения этого чата.",

    # Runs
    "Run succeeded": "Запуск завершён успешно",
    "Run failed": "Запуск завершился ошибкой",
    "Run interrupted": "Запуск прерван",
    "Run status unknown": "Статус запуска неизвестен",
    "Claudexor needs your answer": "Claudexor ожидает ваш ответ",
    "Answer delivered": "Ответ отправлен",
    "Question closed — run cancelled": "Вопрос закрыт — запуск отменён",
    "Question timed out — continuing with assumptions": "Время ожидания ответа истекло — выполнение продолжено с допущениями",

    # Apply/result
    "Applied": "Применено",
    "Applied as branch": "Применено как ветка",
    "Committed": "Создан коммит",
    "PR opened": "Pull Request открыт",
    "Nothing to apply": "Нет изменений для применения",
    "Conflict — apply refused": "Конфликт — применение отклонено",
    "Apply rejected": "Применение отклонено",

    # Workspace / project
    "Runs": "Запуски",
    "No project": "Без проекта",
    "No project output in this thread": "В этом чате пока нет результатов проекта",
    "This thread hasn't produced changes, artifacts, or evidence yet.": "В этом чате ещё нет изменений, артефактов или результатов.",
    "No run in this thread produced a patch.": "Ни один запуск в этом чате не создал изменений.",
    "Run folder": "Папка запуска",
    "Thread title": "Название чата",

    # Artifact / loading
    "Empty file": "Пустой файл",
    "(empty file)": "(пустой файл)",
    "Loading…": "Загрузка…",

    # Auth
    "Sign-in code": "Код входа",
    "Complete the sign-in in your browser to finish.": "Завершите вход в браузере.",
    "Engine offline: reconnect before storing a key.": "Движок не подключён — переподключитесь перед сохранением ключа.",
    "Wait for the current action to finish.": "Дождитесь завершения текущего действия.",
    "Enter the API key in the fallback field first.": "Сначала введите API-ключ в резервное поле.",
    "The sign-in window closed. Get a new link first.": "Окно входа закрыто. Сначала получите новую ссылку.",
    "Delivering the code to the sign-in…": "Передача кода для входа…",
    "Paste the code from the sign-in page first.": "Сначала вставьте код со страницы входа.",
    "Log in": "Войти",
    "Retry check": "Повторить проверку",
    "Store key": "Сохранить ключ",
    "Reconnect": "Переподключить",
    "Done": "Готово",
    "Queued": "В очереди",
    "Launching the native login…": "Запуск нативного входа…",
    "Waiting for you to finish the login": "Ожидание завершения входа",
    "Verifying the session…": "Проверка сессии…",
    "Cancelling…": "Отмена…",
    "Working…": "Выполняется…",
    "Login verified": "Вход подтверждён",
    "Login failed": "Ошибка входа",
    "Cancelled": "Отменено",
    "Timed out waiting for the login": "Истекло время ожидания входа",
    "Not supported for this harness": "Не поддерживается этим агентом",
    "Process termination is unconfirmed": "Завершение процесса не подтверждено",
    "Setup state is still resolving": "Состояние настройки всё ещё определяется",
    "Native login is still active": "Нативный вход всё ещё выполняется",

    # SSH / remote
    "Connecting with OpenSSH…": "Подключение через OpenSSH…",
    "SSH needs authentication. Click Connect to open its terminal.": "Требуется авторизация SSH. Нажмите «Подключить», чтобы открыть терминал.",
    "Preparing the SSH authentication terminal…": "Подготовка терминала авторизации SSH…",
    "Finish SSH authentication in the terminal.": "Завершите авторизацию SSH в терминале.",
    "Installing the remote runtime…": "Установка удалённой среды выполнения…",
    "Updating an incompatible runtime…": "Обновление несовместимой среды выполнения…",
    "Updating the remote runtime…": "Обновление удалённой среды выполнения…",
    "Interactive SSH authentication did not finish.": "Интерактивная авторизация SSH не была завершена.",
    "Disconnected. Cached thread titles remain available.": "Соединение разорвано. Сохранённые названия чатов остаются доступны.",
    "Downloading and verifying the signed runtime…": "Загрузка и проверка подписанной среды выполнения…",
    "The SSH tunnel is unavailable. Reconnect the host.": "SSH-туннель недоступен. Переподключите хост.",
    "SSH needs authentication. Close the current terminal and click Connect.": "Требуется авторизация SSH. Закройте текущий терминал и нажмите «Подключить».",

    # Accounts
    "Scoped limits": "Ограничения модели",
    "Accounts": "Аккаунты",
    "Legacy default login": "Старый вход по умолчанию",
    "Accounts and quota are unavailable while the engine is offline.": "Аккаунты и квоты недоступны, пока движок не подключён.",
    "Removed from Claudexor.": "Удалено из Claudexor.",

    # Composer / access
    "Auto": "Авто",
    "Automatic (account pool)": "Автоматически (пул аккаунтов)",
    "Thread default": "Настройка чата",
    "API key": "API-ключ",
    "Read-only intents never write": "Режимы только для чтения не изменяют файлы",
    "How much this turn may touch": "Какой доступ разрешён для этого запуска",
    "Delegate unavailable": "Делегирование недоступно",
    "No automatic expiry": "Без автоматического истечения",
    "Expiry unavailable": "Срок действия недоступен",

    # Review
    "Route verified": "Маршрут подтверждён",
    "Model arg accepted": "Параметр модели принят",
    "Route unverified": "Маршрут не подтверждён",
    "Same-model fallback": "Резерв на ту же модель",
    "Verified final review clean.": "Финальная проверка подтверждена: замечаний нет.",
    "Review produced findings.": "Проверка выявила замечания.",
    "Review is running.": "Проверка выполняется.",
    "Review failed.": "Проверка завершилась ошибкой.",
    "Review ended with an error.": "Проверка завершилась с ошибкой.",
    "Not reviewed.": "Не проверено.",

    # Output facts
    "Subscription": "Подписка",
    "Output pending": "Результат ожидается",
    "Output finalizing": "Результат формируется",
    "Diagnostic output": "Диагностический результат",
    "Output ready": "Результат готов",

    # Outcome
    "Council": "Совет агентов",
    "Candidates": "Кандидаты",
    "Plan": "План",
    "Cross-family review": "Перекрёстная проверка агентами",

    # Misc
    "Thinking": "Размышление",
    "Appearance": "Внешний вид",
    "Applied to project": "Применено к проекту",
    "Open in workspace": "Открыть в рабочем пространстве",
    "Answer required": "Требуется ответ",
}


def swift_escape(value: str) -> str:
    return (
        value
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


# -------------------------------------------------------
# 1. Extend LocalizedPresentation
# -------------------------------------------------------

mapper = MAPPER.read_text()

marker = """        default:
            return value
"""

if marker not in mapper:
    raise SystemExit("LocalizedPresentation default block not found")

cases = []

for en, ru in TRANSLATIONS.items():
    escaped_en = swift_escape(en)
    escaped_ru = swift_escape(ru)

    # Don't duplicate existing mapper cases.
    if f'case "{escaped_en}":' in mapper:
        continue

    cases.append(
        f'        case "{escaped_en}": return "{escaped_ru}"'
    )

if cases:
    mapper = mapper.replace(
        marker,
        "\n".join(cases) + "\n\n" + marker,
        1
    )
    MAPPER.write_text(mapper)
    print(f"mapper cases added: {len(cases)}")
else:
    print("mapper: no new cases")


# -------------------------------------------------------
# 2. Wrap exact static UI/presentation literals
# -------------------------------------------------------

changed_files = 0
replaced = 0

for path in APP.rglob("*.swift"):
    if path.name == "LocalizedPresentation.swift":
        continue

    text = path.read_text()
    old = text

    for en in TRANSLATIONS:
        escaped = swift_escape(en)
        literal = f'"{escaped}"'
        wrapped = f'LocalizedPresentation.text("{escaped}")'

        # Already localized on this exact occurrence.
        if literal not in text:
            continue

        # Exact literal replacement is intentional here:
        # dictionary contains only user-facing phrases, never wire IDs.
        count = text.count(literal)

        if count:
            text = text.replace(literal, wrapped)
            replaced += count

    if text != old:
        path.write_text(text)
        changed_files += 1
        print("patched:", path.relative_to(APP))


print()
print(f"Pass 11 complete. Changed files: {changed_files}")
print(f"Presentation literals replaced: {replaced}")
