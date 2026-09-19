#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"
MAPPER = APP / "LocalizedPresentation.swift"

T = {
    "Retired external sandbox (full)": "Устаревшая внешняя песочница (полный доступ)",
    "Choose an active access profile for this historical thread before continuing.":
        "Перед продолжением выберите действующий профиль доступа для этого старого чата.",

    "Add a second Claude, Codex, or agy account to control auto-switch here; Cursor accounts already switch automatically at a vendor limit.":
        "Добавьте второй аккаунт Claude, Codex или agy для управления автопереключением; аккаунты Cursor переключаются автоматически при достижении лимита.",
    "Harnesses disagree (—) — pick a mode to set them all consistently.":
        "Настройки агентов различаются (—) — выберите режим, чтобы установить одинаковое значение для всех.",
    "Subscription accounts switch to another enabled account at their quota limit; metered API keys stop instead.":
        "Аккаунты по подписке переключаются на другой включённый аккаунт при достижении квоты; тарифицируемые API-ключи вместо этого останавливаются.",
    "When one account hits its quota, runs continue on another enabled account of the same harness.":
        "Когда один аккаунт достигает квоты, выполнение продолжается на другом включённом аккаунте того же агента.",
    "Runs stop at a quota limit instead of switching accounts.":
        "При достижении квоты выполнение останавливается без переключения аккаунта.",

    "Engine offline — reconnect to remove an account.":
        "Движок не подключён — переподключитесь, чтобы удалить аккаунт.",
    "Engine offline — reconnect to change the account.":
        "Движок не подключён — переподключитесь, чтобы изменить аккаунт.",
    "Removed from Claudexor. Claudexor removed the binding and any Claudexor-owned state or managed secret; it did not change any vendor credential for this OS user.":
        "Удалено из Claudexor. Привязка, состояние Claudexor и управляемые секреты удалены; учётные данные провайдера для пользователя macOS не изменялись.",

    "This engine build does not support threads. Update Claudexor.":
        "Эта версия движка не поддерживает чаты. Обновите Claudexor.",
    "The engine is out of date — restart the daemon.":
        "Движок устарел — перезапустите демон.",
    "Cannot reach the engine — is the daemon running?":
        "Не удалось подключиться к движку — демон запущен?",
    "The files changed after this turn (a later run or a manual edit) —":
        "Файлы изменились после этого запуска (другим запуском или вручную) —",
    "Engine offline: reconnect before answering.":
        "Движок не подключён — переподключитесь перед ответом.",

    "A previous process may still be alive. New Login and Retry stay disabled until the daemon can prove a safe replacement. API-key storage remains a separate operation.":
        "Предыдущий процесс всё ещё может выполняться. Новый вход и повтор отключены, пока демон не подтвердит безопасную замену. Сохранение API-ключа остаётся отдельным действием.",
    "Deadline reached — waiting for the engine's terminal result":
        "Время ожидания истекло — ожидается итоговый результат движка",

    "Login is unavailable until setup state resolves (an active job, recovery, or an unconfirmed prior process).":
        "Вход недоступен, пока не определится состояние настройки (активная задача, восстановление или неподтверждённый предыдущий процесс).",
    "Run a fresh, non-cached Harness Doctor probe.":
        "Запустить новую проверку Harness Doctor без использования кэша.",
    "Store the API key entered in the fallback field below.":
        "Сохранить API-ключ, введённый ниже в резервном поле.",
    "Re-establish setup truth (re-snapshot the job / prove the process gone).":
        "Повторно проверить состояние настройки и подтвердить завершение процесса.",
    "Close this auth sheet.": "Закрыть окно авторизации.",
    "Keep Running closes this sheet without claiming the process stopped. Cancel asks the daemon again and closes only after termination is confirmed. Stay keeps the recovery details visible.":
        "«Продолжить выполнение» закрывает окно, не утверждая, что процесс остановлен. «Отмена» повторно запрашивает демон и закрывает окно только после подтверждения завершения. «Остаться» оставляет сведения о восстановлении открытыми.",
    "Claudexor cannot yet prove whether a setup job is active. Keep Running leaves any accepted job in the background. Cancel first reconciles server state and closes only after confirmed termination.":
        "Claudexor пока не может определить, активна ли задача настройки. «Продолжить выполнение» оставляет принятую задачу в фоне. «Отмена» сначала сверяет состояние сервера и закрывает окно только после подтверждения завершения.",
    "Keep Running closes this sheet while the daemon job continues. Cancel Login waits for confirmed process termination before closing.":
        "«Продолжить выполнение» закрывает окно, пока задача демона продолжает работать. «Отменить вход» ждёт подтверждённого завершения процесса.",

    "Go": "Перейти",
    "localhost:3000  ·  or a URL…": "localhost:3000  ·  или URL…",

    "No available harness lane can receive the selected attachments.":
        "Ни один доступный агент не может принять выбранные вложения.",
    "the file could not be read": "файл не удалось прочитать",
    "it is not a regular file": "это не обычный файл",
    "its size could not be determined": "не удалось определить размер файла",
    "the file changed while it was being read": "файл изменился во время чтения",
    "Remove attachment": "Удалить вложение",

    "This historical thread used a retired access profile. Choose an active profile to continue.":
        "Этот старый чат использовал устаревший профиль доступа. Выберите действующий профиль для продолжения.",
    "Browser keeps this access scope; unsupported harness combinations are refused before launch.":
        "Браузер использует тот же уровень доступа; неподдерживаемые комбинации агентов отклоняются до запуска.",

    "e.g. npm test": "например npm test",
    "model (optional, e.g. opus)": "модель (необязательно, например opus)",
    "claude=opus:max, cursor (or pinned JSON)": "claude=opus:max, cursor (или закреплённый JSON)",
    "path glob (e.g. test/**)": "шаблон пути (например test/**)",
    "reason (optional)": "причина (необязательно)",

    "One candidate with optional model review; completed changes can be applied normally.":
        "Один кандидат с необязательной проверкой моделью; завершённые изменения можно применить обычным способом.",
    "N candidates in isolated envelopes, cross-reviewed, best wins.":
        "Несколько кандидатов в изолированных средах с перекрёстной проверкой; выбирается лучший.",
    "One envelope repaired until gates/review are clean.":
        "Одна среда дорабатывается до прохождения всех проверок.",
    "Scaffold a brand-new repo or component.":
        "Создать новый репозиторий или компонент с нуля.",

    "Budget cap must be a non-negative number (in ⋯)":
        "Лимит бюджета должен быть неотрицательным числом (в ⋯).",
    "Accept risk & unblock": "Принять риск и разблокировать",
    "Rerun with feedback": "Перезапустить с обратной связью",

    "This runtime cannot host the Delegate tool belt. Update or repair the Claudexor runtime, then reconnect.":
        "Эта среда выполнения не поддерживает инструменты делегирования. Обновите или восстановите Claudexor и переподключитесь.",
    "The selected harness cannot accept the Delegate tool belt. Choose a supported harness.":
        "Выбранный агент не поддерживает инструменты делегирования. Выберите поддерживаемого агента.",
    "Delegate is unavailable for the selected harness and runtime. Check Harness Doctor, then try again.":
        "Делегирование недоступно для выбранного агента и среды выполнения. Проверьте Harness Doctor и повторите попытку.",
    "The selected Claudexor runtime could not provide the Delegate tool belt. Update or repair the runtime, then try again.":
        "Выбранная среда Claudexor не предоставила инструменты делегирования. Обновите или восстановите среду и повторите попытку.",
    "The selected harness could not accept the Delegate tool belt. Choose a supported harness, then try again.":
        "Выбранный агент не смог принять инструменты делегирования. Выберите поддерживаемого агента и повторите попытку.",
    "The selected access profile could not host Delegate. Choose Full access, then try again.":
        "Выбранный профиль доступа не позволяет делегирование. Выберите полный доступ и повторите попытку.",
    "One selected lane could not host Delegate and continued as ordinary Agent. Inspect that lane or choose only Delegate-capable harnesses.":
        "Один выбранный агент не поддержал делегирование и продолжил работу как обычный агент. Проверьте этот маршрут или выберите только агентов с поддержкой Delegate.",
    "Delegate could not be enabled before the run started.":
        "Делегирование не удалось включить до начала запуска.",

    "Delegated Claudexor run": "Делегированный запуск Claudexor",
    "Open parent run": "Открыть родительский запуск",

    "Native login setup": "Настройка нативного входа",
    "Smoke Test Ask": "Тестовый запрос",
    "Up": "Вверх",

    "The engine refused to serve this file.":
        "Движок отказался предоставить этот файл.",

    "The latest release has no runtime-manifest.json asset.":
        "В последнем релизе отсутствует runtime-manifest.json.",
    "The runtime manifest could not be parsed.":
        "Не удалось прочитать манифест среды выполнения.",
    "The unpacked runtime is missing its daemon script.":
        "В распакованной среде отсутствует скрипт демона.",
    "The engine is busy running jobs; the update will retry when idle.":
        "Движок занят выполнением задач; обновление повторится после освобождения.",
    "The exact prior engine identity could not be verified; the running engine was not stopped.":
        "Не удалось точно подтвердить предыдущую версию движка; работающий движок не был остановлен.",
    "Another engine lifecycle action is already in progress; retry the update.":
        "Уже выполняется другая операция с движком; повторите обновление позже.",
    "Another runtime update is already in progress.":
        "Уже выполняется другое обновление среды.",
    "no exact identity": "точная идентификация недоступна",

    "Could not refresh accounts and readiness":
        "Не удалось обновить аккаунты и состояние готовности",
    "Copy message": "Копировать сообщение",

    "Run Again requires an explicit access choice.":
        "Для повторного запуска необходимо явно выбрать уровень доступа.",
    "Clear run filter": "Сбросить фильтр запуска",

    "Plan — no files changed": "План — файлы не изменялись",
    "Choose access in composer": "Выберите уровень доступа в поле сообщения",
    "Implemented over open plan questions — plan readiness was overridden.":
        "Реализация выполнена при наличии открытых вопросов плана — проверка готовности плана была переопределена.",
}


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


mapper = MAPPER.read_text()

marker = """        default:
            return value
"""

if marker not in mapper:
    raise SystemExit("LocalizedPresentation default block not found")

new_cases = []

for en, ru in T.items():
    een = esc(en)
    eru = esc(ru)

    if f'case "{een}":' not in mapper:
        new_cases.append(f'        case "{een}": return "{eru}"')

if new_cases:
    mapper = mapper.replace(
        marker,
        "\n".join(new_cases) + "\n\n" + marker,
        1
    )
    MAPPER.write_text(mapper)
    print(f"mapper cases added: {len(new_cases)}")


changed = 0
replaced = 0

for path in APP.rglob("*.swift"):
    if path.name == "LocalizedPresentation.swift":
        continue

    text = path.read_text()
    old = text

    for en in T:
        literal = f'"{esc(en)}"'
        wrapped = f'LocalizedPresentation.text("{esc(en)}")'

        count = text.count(literal)
        if count:
            text = text.replace(literal, wrapped)
            replaced += count

    if text != old:
        path.write_text(text)
        changed += 1
        print("patched:", path.relative_to(APP))

print()
print(f"Pass 12 complete. Changed files: {changed}")
print(f"Presentation literals replaced: {replaced}")
