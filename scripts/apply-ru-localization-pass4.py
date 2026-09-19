#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"

quota = APP / "QuotaViews.swift"
s = quota.read_text()
old = s

# Refresh
s = s.replace(
    'Label("Refresh", systemImage: "arrow.clockwise")',
    'Label(L10n.t("Refresh"), systemImage: "arrow.clockwise")'
)

# Subscription / API key / Local приходят динамически из ClaudexorKit.
s = s.replace(
    'Text(group.routeLabel).foregroundStyle(.secondary)',
    'Text(L10n.t(group.routeLabel)).foregroundStyle(.secondary)'
)

# Нормализуем только отображаемое название окна квоты.
old_func = '''    private func windowLabel(_ window: QuotaPresentation.Window) -> String {
        guard let models = window.appliesToModels, !models.isEmpty else { return window.label }
        return "\\(window.label) · \\(QuotaPresentation.modelScopeLabel(models))"
    }
'''

new_func = '''    private func windowLabel(_ window: QuotaPresentation.Window) -> String {
        let label = localizedQuotaWindowLabel(window.label)

        guard let models = window.appliesToModels, !models.isEmpty else {
            return label
        }

        return "\\(label) · \\(QuotaPresentation.modelScopeLabel(models))"
    }

    private func localizedQuotaWindowLabel(_ raw: String) -> String {
        let normalized = raw
            .lowercased()
            .trimmingCharacters(in: .whitespacesAndNewlines)

        switch normalized {
        case "5 hour", "5 hours", "5h":
            return "5 часов"
        case "7 day", "7 days", "7d", "week", "weekly":
            return "7 дней"
        case "30 day", "30 days", "30d", "month", "monthly":
            return "30 дней"
        default:
            return raw
        }
    }
'''

if old_func in s:
    s = s.replace(old_func, new_func)
else:
    print("WARNING: windowLabel block already changed or not found")

if s != old:
    quota.write_text(s)
    print("patched: QuotaViews.swift")
else:
    print("QuotaViews.swift: no changes")
