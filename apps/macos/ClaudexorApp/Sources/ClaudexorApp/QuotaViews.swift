import SwiftUI
import ClaudexorKit

// The always-expanded sidebar quota footer (`QuotaFooterView`) was replaced by
// the compact bottom-left accounts popover (see `AccountsPopover.swift`, INV-135).
// The full per-window quota detail lives on in `QuotaDetailView`, reached from
// that popover's "All quota windows" affordance.

/// The detail popover mirrors the SAME grouped projection (one section per
/// route group — a cooldown never duplicates the subject into a second card),
/// plus per-snapshot provenance the footer has no room for.
struct QuotaDetailView: View {
    @Environment(AppModel.self) private var model
    @State private var quotaSubscription: AccountsQuotaSubscription?

    private var groups: [QuotaPresentation.Group] {
        QuotaPresentation.groups(from: model.activeQuotaResponse?.snapshots ?? [])
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Theme.Spacing.md) {
                HStack {
                    Text(L10n.t("Quota")).font(.headline)
                    Spacer()
                    Button { Task { _ = await model.refreshAccounts() } } label: {
                        Label(L10n.t("Refresh"), systemImage: "arrow.clockwise")
                    }
                    .buttonStyle(.bordered)
                    .disabled(model.activeAccountsLoadState == .loading)
                }
                displayNotice
                if !groups.isEmpty {
                    ForEach(groups) { group in
                        groupSection(group)
                    }
                } else if model.gateway(for: model.activeExecutionLocation) == nil {
                    ContentUnavailableView(LocalizedPresentation.text("Engine offline"), systemImage: "wifi.slash")
                } else if case .failed(let message) = model.activeAccountsLoadState {
                    failedWithoutGroups(message)
                } else {
                    ContentUnavailableView(
                        "Quota unknown",
                        systemImage: "gauge.with.dots.needle.0percent",
                        description: Text(L10n.t("No official quota snapshot is available yet. Unknown is not shown as full headroom."))
                    )
                }
            }
            .padding(Theme.Spacing.lg)
        }
        .onAppear {
            guard quotaSubscription == nil else { return }
            quotaSubscription = model.beginAccountsQuotaSubscription()
        }
        .onDisappear {
            if let quotaSubscription { model.endAccountsQuotaSubscription(quotaSubscription) }
            quotaSubscription = nil
        }
        .onChange(of: model.activeExecutionLocation) { _, locationID in
            if let quotaSubscription { model.endAccountsQuotaSubscription(quotaSubscription) }
            quotaSubscription = model.beginAccountsQuotaSubscription(locationID: locationID)
        }
    }

    @ViewBuilder private var displayNotice: some View {
        if model.activeAccountsLoadState == .loading, model.activeQuotaResponse != nil {
            Label(L10n.t("Refreshing · last-known quota remains visible"), systemImage: "arrow.clockwise")
                .font(.caption).foregroundStyle(.secondary)
        }
        switch model.activeAccountsQuotaDisplayState {
        case .idle:
            EmptyView()
        case .loading:
            Label(L10n.t("Loading quota…"), systemImage: "arrow.clockwise")
                .font(.caption).foregroundStyle(.secondary)
        case .current:
            EmptyView()
        case .stale(let reason, let observedAt):
            Label(
                "Stale\(observedAt.flatMap(formattedDate).map { " · observed \($0)" } ?? "") · \(reason)",
                systemImage: "exclamationmark.arrow.triangle.2.circlepath")
                .font(.caption).foregroundStyle(Theme.status(.caution))
        case .failedWithoutData(let reason):
            Label(reason, systemImage: "exclamationmark.triangle.fill")
                .font(.caption).foregroundStyle(Theme.status(.negative))
        }
        if case .failed(let message) = model.activeAccountsLoadState,
           model.activeQuotaResponse != nil
        {
            HStack {
                Label(message, systemImage: "exclamationmark.triangle.fill")
                    .font(.caption).foregroundStyle(Theme.status(.negative))
                Spacer()
                Button(L10n.t("Retry")) { Task { _ = await model.refreshAccounts() } }
                    .buttonStyle(.bordered).controlSize(.small)
            }
        }
    }

    private func failedWithoutGroups(_ message: String) -> some View {
        VStack(spacing: Theme.Spacing.sm) {
            ContentUnavailableView(
                "Could not refresh quota",
                systemImage: "exclamationmark.triangle.fill",
                description: Text(message)
            )
            Button(L10n.t("Retry")) { Task { _ = await model.refreshAccounts() } }
                .buttonStyle(.borderedProminent)
        }
    }

    private func groupSection(_ group: QuotaPresentation.Group) -> some View {
        VStack(alignment: .leading, spacing: Theme.Spacing.sm) {
            HStack {
                Text(group.harness).font(.headline)
                if let subject = group.subjectId { Text(subject).foregroundStyle(Theme.accent) }
                Text(L10n.t(group.routeLabel)).foregroundStyle(.secondary)
                if let plan = group.planLabel { Text(plan).foregroundStyle(.secondary) }
                Spacer()
                Text(L10n.t(group.freshness.capitalized))
                    .font(.caption)
                    .foregroundStyle(freshnessColor(group.freshness))
            }
            if let availability = group.availability, availability.state != "available" {
                Label(
                    availability.state == "exhausted" ? L10n.t("Account quota exhausted") : L10n.t("Account cooling down"),
                    systemImage: availability.state == "exhausted" ? "gauge.with.dots.needle.100percent" : "hourglass")
                    .font(.caption)
                    .foregroundStyle(Theme.status(.caution))
            }
            ForEach(group.scopedExhaustions) { scoped in
                Label("\(scoped.scopeLabel) exhausted", systemImage: "scope")
                    .font(.caption)
                    .foregroundStyle(Theme.status(.caution))
            }
            if let cooldown = formattedDate(group.cooldownUntil) {
                Label("Ожидание восстановления до \(cooldown)", systemImage: "hourglass")
                    .font(.caption)
                    .foregroundStyle(.orange)
            }
            ForEach(group.windows) { window in
                VStack(alignment: .leading, spacing: Theme.Spacing.xxs) {
                    HStack {
                        Text(windowLabel(window))
                        Spacer()
                        Text(usageText(window.usedRatio)).monospacedDigit()
                    }
                    if let ratio = window.usedRatio {
                        ProgressView(value: ratio, total: 1).tint(ratio >= 0.9 ? .orange : Theme.accent)
                    } else {
                        Text(L10n.t("Provider did not report usage for this window."))
                            .font(.caption2).foregroundStyle(.secondary)
                    }
                    if let reset = formattedDate(window.resetsAt) {
                        Text("Сброс \(reset)")
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                    }
                }
                .padding(Theme.Spacing.sm)
                .background(Theme.surfaceRaised, in: RoundedRectangle(cornerRadius: Theme.Radius.control))
            }
            ForEach(group.sources) { source in
                Text("\(source.source.replacingOccurrences(of: "_", with: " ")) · получено \(formattedDate(source.observedAt) ?? source.observedAt)")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private func windowLabel(_ window: QuotaPresentation.Window) -> String {
        let label = localizedQuotaWindowLabel(window.label)

        guard let models = window.appliesToModels, !models.isEmpty else {
            return label
        }

        return "\(label) · \(QuotaPresentation.modelScopeLabel(models))"
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
        case "1 reset credit available":
            return "Доступен 1 сброс лимита"
        case "reset credit available":
            return "Доступен сброс лимита"
        default:
            return raw
        }
    }
}

private func usageText(_ ratio: Double?) -> String {
    guard let ratio else { return L10n.t("Unknown") }
    return "Использовано \(Int((ratio * 100).rounded()))%"
}

private func freshnessColor(_ freshness: String) -> Color {
    switch freshness {
    case "fresh": return Theme.status(.positive)
    case "stale": return Theme.status(.caution)
    default: return .secondary
    }
}

func formattedDate(_ value: String?) -> String? {
    guard let value else { return nil }
    let fractional = ISO8601DateFormatter()
    fractional.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
    let plain = ISO8601DateFormatter()
    guard let date = fractional.date(from: value) ?? plain.date(from: value) else { return value }
    return date.formatted(
        Date.FormatStyle(date: .abbreviated, time: .shortened)
            .locale(Locale(identifier: "ru_RU")))
}
