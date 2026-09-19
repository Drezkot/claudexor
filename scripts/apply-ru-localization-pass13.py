#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"
MAPPER = APP / "LocalizedPresentation.swift"

T = {
    "The files changed after this turn (a later run or a manual edit) —":
        "Файлы изменились после этого запуска (другим запуском или вручную) —",

    "Native login setup":
        "Настройка нативного входа",

    "Smoke Test Ask":
        "Тестовый запрос",

    "Up":
        "Вверх",

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

    "no exact identity":
        "точная идентификация недоступна",

    "Could not refresh accounts and readiness":
        "Не удалось обновить аккаунты и состояние готовности",

    "Copy message":
        "Копировать сообщение",

    "Run Again requires an explicit access choice.":
        "Для повторного запуска необходимо явно выбрать уровень доступа.",

    "Clear run filter":
        "Сбросить фильтр запуска",

    "Plan — no files changed":
        "План — файлы не изменялись",

    "Choose access in composer":
        "Выберите уровень доступа в поле сообщения",

    "Implemented over open plan questions — plan readiness was overridden.":
        "Реализация выполнена при наличии открытых вопросов плана — проверка готовности плана была переопределена.",

    "Accept risk & unblock":
        "Принять риск и разблокировать",

    "Rerun with feedback":
        "Перезапустить с обратной связью",

    "Delegated Claudexor run":
        "Делегированный запуск Claudexor",

    "Open parent run":
        "Открыть родительский запуск",
}


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


# Добавляем недостающие случаи в mapper.
mapper = MAPPER.read_text()

marker = """        default:
            return value
"""

if marker not in mapper:
    raise SystemExit("LocalizedPresentation default block not found")

cases = []

for en, ru in T.items():
    een = esc(en)
    eru = esc(ru)

    if f'case "{een}":' not in mapper:
        cases.append(f'        case "{een}": return "{eru}"')

if cases:
    mapper = mapper.replace(
        marker,
        "\n".join(cases) + "\n\n" + marker,
        1,
    )
    MAPPER.write_text(mapper)
    print(f"mapper cases added: {len(cases)}")
else:
    print("mapper cases added: 0")


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
print(f"Pass 13 complete. Changed files: {changed}")
print(f"Presentation literals replaced: {replaced}")
