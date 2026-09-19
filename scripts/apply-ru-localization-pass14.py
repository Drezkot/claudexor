#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"


PATCHES = {
    # ---------------------------------------------------------
    # Thread workspace
    # ---------------------------------------------------------
    "ThreadWorkspacePanel.swift": [
        (
            'Text("Thread workspace — \\(detail.thread.title ?? "Untitled thread")")',
            'Text("Рабочее пространство чата — \\(detail.thread.title ?? "Без названия")")'
        ),
        (
            'Text("run: \\(String(id.suffix(6)))")',
            'Text("запуск: \\(String(id.suffix(6)))")'
        ),
        (
            '.help("Filtered to full run id \\(id) — clear to see the whole thread\'s workspace")',
            '.help("Показан запуск \\(id) — сбросьте фильтр, чтобы увидеть рабочее пространство всего чата")'
        ),
    ],

    # ---------------------------------------------------------
    # Markdown / rendered output
    # ---------------------------------------------------------
    "MarkdownOutputView.swift": [
        (
            'Text("\\(renderTruncated) more characters not rendered here — open the run\'s full answer artifact.")',
            'Text("Ещё \\(renderTruncated) символов не показано — откройте полный артефакт ответа запуска.")'
        ),
        (
            'linkRefusal = "Link not opened: \\(reason)."',
            'linkRefusal = "Ссылка не открыта: \\(reason)."'
        ),
        (
            'parts.append("\\(table.truncatedRows) more rows")',
            'parts.append("ещё строк: \\(table.truncatedRows)")'
        ),
        (
            'parts.append("\\(table.truncatedColumns) more columns")',
            'parts.append("ещё столбцов: \\(table.truncatedColumns)")'
        ),
    ],

    # ---------------------------------------------------------
    # Streams / quota switching
    # ---------------------------------------------------------
    "AppModel+Streams.swift": [
        (
            '"Question: \\(String(summary.prefix(200)))"',
            '"Вопрос: \\(String(summary.prefix(200)))"'
        ),
        (
            '"Switched to account \\(to)\\(harness.isEmpty ? "" : " (\\(harness))") — quota limit"',
            '"Переключено на аккаунт \\(to)\\(harness.isEmpty ? "" : " (\\(harness))") — достигнута квота"'
        ),
        (
            '"Account quota headroom exceeded\\(harness.isEmpty ? "" : " (\\(harness))")"',
            '"Резерв квоты аккаунта исчерпан\\(harness.isEmpty ? "" : " (\\(harness))")"'
        ),
        (
            '"No eligible account has quota headroom\\(harness.isEmpty ? "" : " (\\(harness))")"',
            '"Нет подходящего аккаунта с доступной квотой\\(harness.isEmpty ? "" : " (\\(harness))")"'
        ),
    ],

    "AppModel+AccountsQuotaDisplay.swift": [
        (
            '"Rate-limit cooldown: \\(vendors) served from last-known data (not re-fetched)."',
            '"Ожидание после ограничения запросов: \\(vendors) показаны по последним известным данным без повторного запроса."'
        ),
    ],

    # ---------------------------------------------------------
    # Remote actions
    # ---------------------------------------------------------
    "AppModel+RemoteActions.swift": [
        (
            'title: "\\(HarnessFamily(rawValue: harness.rawValue).label) login — \\(connection.displayName)"',
            'title: "Вход \\(HarnessFamily(rawValue: harness.rawValue).label) — \\(connection.displayName)"'
        ),
        (
            '"\\(HarnessFamily(rawValue: harness.rawValue).label) sign-in started."',
            '"Вход \\(HarnessFamily(rawValue: harness.rawValue).label) запущен."'
        ),
        (
            '"Harness Doctor: \\(ready) of \\(harnesses.count) harnesses ready."',
            '"Harness Doctor: готово агентов \\(ready) из \\(harnesses.count)."'
        ),
        (
            '"\\(harness) is not an installable harness; nothing was installed."',
            '"\\(harness) нельзя установить как агент; ничего не установлено."'
        ),
        (
            'title: "Install \\(HarnessFamily(rawValue: prompt.harness).label) — \\(connection.displayName)"',
            'title: "Установка \\(HarnessFamily(rawValue: prompt.harness).label) — \\(connection.displayName)"'
        ),
        (
            '"\\(displayName) installer failed with exit code \\(exitCode)."',
            '"Установщик \\(displayName) завершился с кодом \\(exitCode)."'
        ),
        (
            '"\\(displayName) installed, but the remote connection is unavailable for Harness Doctor."',
            '"\\(displayName) установлен, но удалённое подключение недоступно для Harness Doctor."'
        ),
        (
            '"\\(displayName) installed, but Harness Doctor could not refresh. Retry."',
            '"\\(displayName) установлен, но Harness Doctor не смог обновить состояние. Повторите попытку."'
        ),
        (
            '"\\(displayName) installed and ready."',
            '"\\(displayName) установлен и готов."'
        ),
        (
            '"Use Login → \\(displayName)."',
            '"Используйте «Вход» → \\(displayName)."'
        ),
        (
            '"\\(label) account is signed in and ready."',
            '"Аккаунт \\(label) авторизован и готов."'
        ),
        (
            '"\\(label) account is not ready yet."',
            '"Аккаунт \\(label) пока не готов."'
        ),
        (
            '"Harness Doctor did not return \\(harnessID)."',
            '"Harness Doctor не вернул данные для \\(harnessID)."'
        ),
        (
            '"\\(label) is signed in and ready."',
            '"\\(label) авторизован и готов."'
        ),
        (
            '"\\(label) is not ready yet."',
            '"\\(label) пока не готов."'
        ),
    ],

    # ---------------------------------------------------------
    # Remote managed login
    # ---------------------------------------------------------
    "RemoteSetupLoginRouting.swift": [
        (
            '"The remote engine did not provide a current managed-login capability for \\(HarnessFamily(rawValue: harness.rawValue).label). Reconnect or refresh Harness Doctor before trying again."',
            '"Удалённый движок не предоставил актуальный способ управляемого входа для \\(HarnessFamily(rawValue: harness.rawValue).label). Переподключитесь или обновите Harness Doctor и повторите попытку."'
        ),
        (
            '"The remote engine reports no managed login for \\(HarnessFamily(rawValue: harness.rawValue).label)."',
            '"Удалённый движок сообщает, что управляемый вход для \\(HarnessFamily(rawValue: harness.rawValue).label) недоступен."'
        ),
    ],

    # ---------------------------------------------------------
    # Artifact UI
    # ---------------------------------------------------------
    "ArtifactGalleryView.swift": [
        (
            '"Failed to load: \\(failedRunIds.joined(separator: ", "))"',
            '"Не удалось загрузить: \\(failedRunIds.joined(separator: ", "))"'
        ),
        (
            '.help("\\(art.path) — click to open full size")',
            '.help("\\(art.path) — нажмите, чтобы открыть в полном размере")'
        ),
        (
            '.help(isText ? "\\(art.path) — open text viewer" : "\\(art.path) — open externally")',
            '.help(isText ? "\\(art.path) — открыть просмотр текста" : "\\(art.path) — открыть во внешнем приложении")'
        ),
        (
            'ProgressView("Loading \\(fileName)…")',
            'ProgressView("Загрузка \\(fileName)…")'
        ),
    ],

    # ---------------------------------------------------------
    # Auth sheet
    # ---------------------------------------------------------
    "AuthSheet.swift": [
        (
            'return "This setup job belongs to \\(owner). Its controls continue that exact login; your selected account is unchanged."',
            'return "Эта задача настройки относится к \\(owner). Управление продолжает именно этот вход; выбранный аккаунт не изменён."'
        ),
        (
            'status = "Engine offline: reconnect before starting \\(family.label) setup."',
            'status = "Движок не подключён — переподключитесь перед настройкой \\(family.label)."'
        ),
        (
            'status = "Cancellation could not be confirmed: \\(next.lastError ?? "unknown error")"',
            'status = "Не удалось подтвердить отмену: \\(next.lastError ?? "неизвестная ошибка")"'
        ),
        (
            'status = "Could not store \\(name); reconnect the local engine and try again."',
            'status = "Не удалось сохранить \\(name); переподключите локальный движок и повторите попытку."'
        ),
        (
            '? "Stored \\(name) and refreshed its exact credential readiness."',
            '? "Сохранено \\(name); состояние учётных данных обновлено."'
        ),
        (
            ': "Stored \\(name), but its exact readiness refresh failed. Use Recheck before relying on it."',
            ': "Сохранено \\(name), но обновить состояние готовности не удалось. Перед использованием выполните повторную проверку."'
        ),
        (
            'status = "Cancellation could not be confirmed: \\(latest.lastError ?? "setup state remains unknown")"',
            'status = "Не удалось подтвердить отмену: \\(latest.lastError ?? "состояние настройки остаётся неизвестным")"'
        ),
        (
            'status = "Cancellation could not be confirmed: \\(latest.lastError ?? "unknown error")"',
            'status = "Не удалось подтвердить отмену: \\(latest.lastError ?? "неизвестная ошибка")"'
        ),
    ],

    # ---------------------------------------------------------
    # Auth UI
    # ---------------------------------------------------------
    "OpsScreens+Auth.swift": [
        (
            '"\\(family.label) signs in only into a named account. Add or open a \\(family.label) account in Accounts to sign in on this remote location."',
            '"\\(family.label) поддерживает вход только в именованный аккаунт. Добавьте или откройте аккаунт \\(family.label) в разделе «Аккаунты» для входа на удалённом хосте."'
        ),
        (
            '"Open \\(family.label) auth details and fallback key management."',
            '"Открыть сведения авторизации \\(family.label) и управление резервным ключом."'
        ),
        (
            '"Open setup/auth actions for \\(family.label)."',
            '"Открыть настройку и авторизацию \\(family.label)."'
        ),
    ],

    # ---------------------------------------------------------
    # Device code
    # ---------------------------------------------------------
    "AuthSheetDeviceCodeCard.swift": [
        (
            '"That link expired before a code arrived. Get a new one below, then paste the code \\(vendor) shows:"',
            '"Ссылка истекла до получения кода. Получите новую ссылку ниже и вставьте код, который покажет \\(vendor):"'
        ),
        (
            '"Open this sign-in link, then paste the code \\(vendor) shows back here:"',
            '"Откройте ссылку для входа и вставьте сюда код, который покажет \\(vendor):"'
        ),
        (
            'Text("Enter this one-time code on the \\(vendor) sign-in page:")',
            'Text("Введите этот одноразовый код на странице входа \\(vendor):")'
        ),
        (
            '.accessibilityLabel("One-time code \\(disclosure.userCode)")',
            '.accessibilityLabel("Одноразовый код \\(disclosure.userCode)")'
        ),
        (
            '"Open the \\(vendor) sign-in page in a private browser session."',
            '"Открыть страницу входа \\(vendor) в приватном окне браузера."'
        ),
        (
            '"Open the \\(vendor) sign-in page in your default browser."',
            '"Открыть страницу входа \\(vendor) в браузере по умолчанию."'
        ),
        (
            'Text("Waiting for \\(vendor)…")',
            'Text("Ожидание \\(vendor)…")'
        ),
        (
            'Label("Code delivered. Waiting for \\(vendor) to finish the sign-in…",',
            'Label("Код отправлен. Ожидание завершения входа \\(vendor)…",'
        ),
        (
            '"Start a fresh \\(vendor) sign-in and show a new link."',
            '"Начать новый вход \\(vendor) и показать новую ссылку."'
        ),
        (
            '"Cancel this sign-in and start a fresh one — only if \\(vendor) refused the code you sent."',
            '"Отменить этот вход и начать новый — только если \\(vendor) отклонил отправленный код."'
        ),
    ],

    # ---------------------------------------------------------
    # Model override
    # ---------------------------------------------------------
    "HarnessModelOverride.swift": [
        (
            '.help("Loading the \\(family.label) model catalog…")',
            '.help("Загрузка каталога моделей \\(family.label)…")'
        ),
        (
            'Text("\\(HarnessModelPresentation.menuTitle(label: nil, id: modelDraft)) (not in \\(models.source) list)")',
            'Text("\\(HarnessModelPresentation.menuTitle(label: nil, id: modelDraft)) (нет в списке \\(models.source))")'
        ),
        (
            'Text("\\(modelDraft) — refused (no truth source)")',
            'Text("\\(modelDraft) — отклонено (нет источника данных)")'
        ),
        (
            'Text("\\(modelDraft) — model catalog unavailable")',
            'Text("\\(modelDraft) — каталог моделей недоступен")'
        ),
        (
            '.help("Reload the \\(family.label) model catalog to verify this override.")',
            '.help("Обновите каталог моделей \\(family.label), чтобы проверить это переопределение.")'
        ),
        (
            '.help("Could not load the \\(family.label) model catalog; the override stays as-is. Retry after reconnecting to verify it.")',
            '.help("Не удалось загрузить каталог моделей \\(family.label); переопределение сохранено без изменений. После переподключения повторите проверку.")'
        ),
        (
            '.help("Reload the \\(family.label) model catalog.")',
            '.help("Обновить каталог моделей \\(family.label).")'
        ),
        (
            '.help("Could not load the \\(family.label) model catalog. Retry after reconnecting.")',
            '.help("Не удалось загрузить каталог моделей \\(family.label). Переподключитесь и повторите попытку.")'
        ),
        (
            '" (verified against CLI \\($0))"',
            '" (проверено через CLI \\($0))"'
        ),
        (
            'return "Model forwarded to \\(family.label); source: \\(models.source)\\(freshness). Harness default keeps the engine choice."',
            'return "Модель передана \\(family.label); источник: \\(models.source)\\(freshness). Значение по умолчанию оставляет выбор движку."'
        ),
        (
            'if loadingModels { return "Loading \\(family.label) models…" }',
            'if loadingModels { return "Загрузка моделей \\(family.label)…" }'
        ),
        (
            'return "\\(family.label) exposes no model truth source, so runs use its default model; an explicit model would be refused (strict model governance)."',
            'return "\\(family.label) не предоставляет источник списка моделей, поэтому используется модель по умолчанию; явное указание модели будет отклонено."'
        ),
    ],

    # ---------------------------------------------------------
    # Pool / attachment help
    # ---------------------------------------------------------
    "HarnessPoolPresentation.swift": [
        (
            '"Auto includes available harnesses; this one is unavailable: \\(availability.reason)"',
            '"Авто включает доступных агентов; этот агент недоступен: \\(availability.reason)"'
        ),
        (
            '"This harness is \\(membership) in the explicit eligible pool, but is unavailable: \\(availability.reason)"',
            '"Этот агент \\(membership) в выбранном пуле, но сейчас недоступен: \\(availability.reason)"'
        ),
        (
            '"\\(accessibilityMembership), unavailable"',
            '"\\(accessibilityMembership), недоступен"'
        ),
    ],

    "ComposerAttachments.swift": [
        (
            '"\\(context); Auto may omit incompatible lanes before launch."',
            '"\\(context); режим «Авто» может исключить несовместимых агентов до запуска."'
        ),
        (
            '"\\(context); every explicit lane must accept the selected content."',
            '"\\(context); каждый явно выбранный агент должен поддерживать выбранное содержимое."'
        ),
        (
            '.help("Remove \\(att.name)")',
            '.help("Удалить \\(att.name)")'
        ),
    ],

    # ---------------------------------------------------------
    # Conversation
    # ---------------------------------------------------------
    "ThreadsScreen+Conversation.swift": [
        (
            '" · live session"',
            '" · активная сессия"'
        ),
        (
            '"Native session \\($0) resumes on the next turn"',
            '"Нативная сессия \\($0) продолжится при следующем сообщении"'
        ),
        (
            '"No native session yet"',
            '"Нативной сессии пока нет"'
        ),
    ],

    # ---------------------------------------------------------
    # Updates
    # ---------------------------------------------------------
    "UpdateChip.swift": [
        (
            '.help("Download, verify, and install engine v\\(update.version) in place")',
            '.help("Загрузить, проверить и установить движок v\\(update.version)")'
        ),
        (
            '.help("Update to v\\(update.version) is available — install in place or download manually.")',
            '.help("Доступно обновление до v\\(update.version) — установите его автоматически или загрузите вручную.")'
        ),
    ],

    "AppModel+RuntimeUpdate.swift": [
        (
            '"Update check failed: \\(error.localizedDescription)"',
            '"Не удалось проверить обновление: \\(error.localizedDescription)"'
        ),
        (
            '"Update available: v\\(manifest.version)"',
            '"Доступно обновление: v\\(manifest.version)"'
        ),
        (
            '"Update status unknown: \\(reason)"',
            '"Статус обновления неизвестен: \\(reason)"'
        ),
        (
            '"Preparing update to v\\(manifest.version)…"',
            '"Подготовка обновления до v\\(manifest.version)…"'
        ),
        (
            '"Could not locate the runtime download for v\\(manifest.version)."',
            '"Не удалось найти пакет среды выполнения v\\(manifest.version)."'
        ),
        (
            '"Updated to engine v\\(version)."',
            '"Движок обновлён до v\\(version)."'
        ),
        (
            '"Update failed: \\(error.localizedDescription)"',
            '"Ошибка обновления: \\(error.localizedDescription)"'
        ),
        (
            '"Update rolled back: \\(reason)."',
            '"Обновление отменено с откатом: \\(reason)."'
        ),
        (
            '"Update failed: \\(reason)."',
            '"Ошибка обновления: \\(reason)."'
        ),
    ],

    # ---------------------------------------------------------
    # Thread lifecycle
    # ---------------------------------------------------------
    "ThreadLifecycle.swift": [
        (
            '"Reconnecting to \\(host)…"',
            '"Переподключение к \\(host)…"'
        ),
        (
            '"Could not reconnect to \\(host)."',
            '"Не удалось переподключиться к \\(host)."'
        ),
        (
            '"Could not load thread: \\(detail)"',
            '"Не удалось загрузить чат: \\(detail)"'
        ),
        (
            '"Apply failed: \\(error)"',
            '"Ошибка применения: \\(error)"'
        ),
        (
            '"Retry failed: \\(userMessage(for: error))"',
            '"Повторная попытка завершилась ошибкой: \\(userMessage(for: error))"'
        ),
        (
            '"Run Again failed: \\(userMessage(for: error))"',
            '"Повторный запуск завершился ошибкой: \\(userMessage(for: error))"'
        ),
    ],

    # ---------------------------------------------------------
    # Settings errors
    # ---------------------------------------------------------
    "AppModel+Settings.swift": [
        (
            '"Could not load settings: \\(self.userMessage(for: error))"',
            '"Не удалось загрузить настройки: \\(self.userMessage(for: error))"'
        ),
        (
            '"Could not save settings: \\(error)"',
            '"Не удалось сохранить настройки: \\(error)"'
        ),
    ],

    # ---------------------------------------------------------
    # Run actions
    # ---------------------------------------------------------
    "AppModel+RunActions.swift": [
        (
            '" Required action: \\($0)."',
            '" Требуемое действие: \\($0)."'
        ),
        (
            '"Request failed (HTTP \\(status), \\(problem.code)): \\(problem.message)\\(action)"',
            '"Ошибка запроса (HTTP \\(status), \\(problem.code)): \\(problem.message)\\(action)"'
        ),
        (
            '"Request failed (HTTP \\(status)): \\(detail)"',
            '"Ошибка запроса (HTTP \\(status)): \\(detail)"'
        ),
        (
            '"Request failed (HTTP \\(status))."',
            '"Ошибка запроса (HTTP \\(status))."'
        ),
        (
            '"Decision was not accepted (\\(res.status))."',
            '"Решение не принято (\\(res.status))."'
        ),
        (
            '"Decision failed: \\(error)"',
            '"Ошибка решения: \\(error)"'
        ),
        (
            '"Revert was refused (\\(res.status))."',
            '"Откат отклонён (\\(res.status))."'
        ),
        (
            '"Answer was not accepted (\\(response.status))."',
            '"Ответ не принят (\\(response.status))."'
        ),
        (
            '"Could not deliver the answer: \\(error)"',
            '"Не удалось отправить ответ: \\(error)"'
        ),
    ],

    # ---------------------------------------------------------
    # Remote connection UI
    # ---------------------------------------------------------
    "RemoteConnectionSettingsViews.swift": [
        (
            'Text("Remote runtime \\(runtime)")',
            'Text("Удалённая среда \\(runtime)")'
        ),
        (
            '"Install the signed Claudexor runtime on \\(connection.displayName)?"',
            '"Установить подписанную среду Claudexor на \\(connection.displayName)?"'
        ),
        (
            '"Remove \\(connection.displayName)?"',
            '"Удалить \\(connection.displayName)?"'
        ),
    ],

    # ---------------------------------------------------------
    # Workspace evidence
    # ---------------------------------------------------------
    "WorkspaceEvidence.swift": [
        (
            'accessibilityName: "Run \\(String(runId.suffix(6))) evidence"',
            'accessibilityName: "Данные запуска \\(String(runId.suffix(6)))"'
        ),
        (
            'Text("Run \\(String(runId.suffix(6)))")',
            'Text("Запуск \\(String(runId.suffix(6)))")'
        ),
    ],

    # ---------------------------------------------------------
    # Council / plan / diff
    # ---------------------------------------------------------
    "RunOutcomeSection.swift": [
        (
            'Text("\\(council.drafted) of \\(council.requested) drafts accepted"',
            'Text("Принято черновиков: \\(council.drafted) из \\(council.requested)"'
        ),
        (
            '" · merged by \\($0)"',
            '" · объединено: \\($0)"'
        ),
        (
            '" · merge did not complete"',
            '" · объединение не завершено"'
        ),
        (
            'Text("\\(task.planDone)/\\(task.plan.count) done")',
            'Text("\\(task.planDone)/\\(task.plan.count) выполнено")'
        ),
    ],

    "DiffView.swift": [
        (
            'Text("\\(files.count) files")',
            'Text("Файлов: \\(files.count)")'
        ),
        (
            'accessibilityName: "Diff of \\(file.path)"',
            'accessibilityName: "Изменения файла \\(file.path)"'
        ),
    ],

    # ---------------------------------------------------------
    # Thread list
    # ---------------------------------------------------------
    "ThreadsScreen+List.swift": [
        (
            'Text("Threads from “\\(URL(fileURLWithPath: problem.root).lastPathComponent)” are hidden — the project folder is missing. Relink it to restore them.")',
            'Text("Чаты проекта «\\(URL(fileURLWithPath: problem.root).lastPathComponent)» скрыты — папка проекта отсутствует. Укажите путь заново, чтобы восстановить их.")'
        ),
        (
            'return "\\(project) · \\(thread.runIds.count) turn\\(thread.runIds.count == 1 ? "" : "s")"',
            'return "\\(project) · запусков: \\(thread.runIds.count)"'
        ),
        (
            'return "\\(base) · synced \\(formattedRemoteSyncTime(cached.syncedAt))"',
            'return "\\(base) · синхронизировано \\(formattedRemoteSyncTime(cached.syncedAt))"'
        ),
    ],

    # ---------------------------------------------------------
    # Account presentation
    # ---------------------------------------------------------
    "AccountsPresentation.swift": [
        (
            'return "A second \\(subject) subscription — one click opens the official CLI login."',
            'return "Вторая подписка \\(subject) — одним нажатием откроется официальный вход через CLI."'
        ),
        (
            'case 2: return "\\(labels[0]) or \\(labels[1])"',
            'case 2: return "\\(labels[0]) или \\(labels[1])"'
        ),
        (
            'default: return labels.dropLast().joined(separator: ", ") + ", or \\(labels[labels.count - 1])"',
            'default: return labels.dropLast().joined(separator: ", ") + " или \\(labels[labels.count - 1])"'
        ),
        (
            'default: return "\\(rows.count) accounts"',
            'default: return "Аккаунтов: \\(rows.count)"'
        ),
    ],

    # ---------------------------------------------------------
    # Composer model section
    # ---------------------------------------------------------
    "ComposerModelsSection.swift": [
        (
            'Text("\\(HarnessModelPresentation.menuTitle(label: nil, id: current)) (not offered here)")',
            'Text("\\(HarnessModelPresentation.menuTitle(label: nil, id: current)) (здесь недоступна)")'
        ),
        (
            '.help("\\(family.label) exposes no model truth source, so this turn uses its default model; an explicit model would be refused (strict model governance).")',
            '.help("\\(family.label) не предоставляет список моделей, поэтому используется модель по умолчанию; явная модель будет отклонена.")'
        ),
        (
            '.help("\\(family.label)\'s models endpoint was unreachable. Retry, or check the engine connection.")',
            '.help("Не удалось получить модели \\(family.label). Повторите попытку или проверьте подключение к движку.")'
        ),
        (
            '.help("Fetching \\(family.label)\'s model truth source; if this persists, the models endpoint is unreachable.")',
            '.help("Получение списка моделей \\(family.label); если сообщение не исчезает, источник моделей недоступен.")'
        ),
        (
            '" (verified against CLI \\($0))"',
            '" (проверено через CLI \\($0))"'
        ),
        (
            '" \\(hiddenOnRoute) model\\(hiddenOnRoute == 1 ? " is" : "s are") hidden on the current auth route."',
            '" Скрыто моделей для текущего маршрута авторизации: \\(hiddenOnRoute)."'
        ),
        (
            'return "Model for \\(family.label) on THIS turn; source: \\(catalog.source)\\(freshness).\\(hidden) Default keeps the harness/settings choice."',
            'return "Модель \\(family.label) для этого запуска; источник: \\(catalog.source)\\(freshness).\\(hidden) Значение по умолчанию использует настройку агента."'
        ),
    ],

    # ---------------------------------------------------------
    # Turn presentation
    # ---------------------------------------------------------
    "TurnPresentation.swift": [
        (
            'identity = "Best-of \\(max(1, n))"',
            'identity = "Лучший из \\(max(1, n))"'
        ),
        (
            'parts.append("Thinking \\(Int(thinkingSeconds))s")',
            'parts.append("Размышление: \\(Int(thinkingSeconds)) с")'
        ),
        (
            'parts.append("\\(tools) tool\\(tools == 1 ? "" : "s")")',
            'parts.append("инструментов: \\(tools)")'
        ),
        (
            'parts.append("\\(files) file\\(files == 1 ? "" : "s")")',
            'parts.append("файлов: \\(files)")'
        ),
    ],

    # ---------------------------------------------------------
    # AppModel visible statuses
    # ---------------------------------------------------------
    "AppModel.swift": [
        (
            'settingsStatus = "Choose a Current Project before launching \\(mode.label). Ask can run without a project."',
            'settingsStatus = "Выберите проект перед запуском \\(mode.label). Режим «Вопрос» может работать без проекта."'
        ),
        (
            '"Queued · \\(mode.label)"',
            '"В очереди · \\(mode.label)"'
        ),
        (
            '"Queued in daemon · \\(info.state)"',
            '"В очереди демона · \\(info.state)"'
        ),
        (
            '"Failed to start: \\(error)"',
            '"Не удалось запустить: \\(error)"'
        ),
        (
            '"Could not create thread: \\(userMessage(for: error))"',
            '"Не удалось создать чат: \\(userMessage(for: error))"'
        ),
    ],
}


changed = 0
replaced = 0
missing = 0

for filename, pairs in PATCHES.items():
    path = APP / filename

    if not path.exists():
        print("missing file:", filename)
        missing += 1
        continue

    text = path.read_text()
    old_text = text
    file_count = 0

    for old, new in pairs:
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            replaced += count
            file_count += count

    if text != old_text:
        path.write_text(text)
        changed += 1
        print(f"patched: {filename} ({file_count})")


print()
print(f"Pass 14 complete. Changed files: {changed}")
print(f"Dynamic UI replacements: {replaced}")
print(f"Missing files: {missing}")
