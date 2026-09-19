import SwiftUI

extension SettingsScreen {
    func settingsTab<Content: View>(
        @ViewBuilder _ content: () -> Content
    ) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: Theme.Spacing.lg) {
                content()
            }
            .padding(.horizontal, Theme.Spacing.xl)
            .padding(.vertical, Theme.Spacing.xl)
            .frame(maxWidth: Theme.Layout.readableMaxWidth, alignment: .leading)
            .frame(maxWidth: .infinity, alignment: .topLeading)
            // QA-076: each pane needs an explicit keyboard-focus cohort.
            .focusSection()
        }
        .scrollContentBackground(.hidden)
        .background(Theme.surfaceBase)
    }

    @ViewBuilder var generalGroup: some View {
        @Bindable var model = model
        settingsGroup(L10n.t("General"), "gearshape") {
            KeyValueRow(
                key: "Engine status",
                value: model.health.label,
                valueColor: model.health == .connected
                    ? Theme.status(.positive)
                    : .secondary
            )
            HStack {
                Button {
                    Task { await model.connect() }
                } label: {
                    Label(L10n.t(LocalizedPresentation.text("Reconnect")), systemImage: "arrow.clockwise")
                }
                .buttonStyle(.bordered)
                .productControlAccessibility(LocalizedPresentation.text("Reconnect"))
                .help("Reconnect the app to the selected engine and reload its current state.")
                Button {
                    Task { await refreshAll() }
                } label: {
                    Label(L10n.t("Refresh metadata"), systemImage: "arrow.triangle.2.circlepath")
                }
                .buttonStyle(.bordered)
                .productControlAccessibility("Refresh metadata")
                .help("Reload settings, quota, secrets, harness readiness, and trust metadata.")
            }
        }
    }

    @ViewBuilder var appearanceGroup: some View {
        @Bindable var model = model
        settingsGroup(L10n.t(LocalizedPresentation.text("Appearance")), "paintpalette") {
            Picker(L10n.t("Theme"), selection: $model.appearance) {
                ForEach(AppearanceMode.allCases) {
                    Label($0.label, systemImage: $0.glyph).tag($0)
                }
            }
            .pickerStyle(.segmented)
            Text(L10n.t("The window is matte glass — the desktop shows faintly through it. Code and diffs stay on a solid surface for contrast. Reduce Transparency falls back to a solid backdrop."))
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }

    @ViewBuilder var routingGroup: some View {
        settingsGroup(L10n.t("Agent & Routing"), "point.3.connected.trianglepath.dotted") {
            HStack {
                Picker(
                    L10n.t("Routing goal"),
                    selection: draftBinding(\.routingGoal, lane: .routingGoal)
                ) {
                    Text(L10n.t(LocalizedPresentation.text("Auto"))).tag("auto")
                    Text(L10n.t("Quality")).tag("quality")
                    Text(L10n.t("Economy")).tag("economy")
                }
                .help("Auto paces expiring quota, Quality uses your highest comparable tier, and Economy minimizes incremental paid spend.")
                laneStatus(.routingGoal)
            }
            HStack {
                Picker(
                    L10n.t("Paid fallback"),
                    selection: draftBinding(\.paidFallback, lane: .paidFallback)
                ) {
                    Text(L10n.t("Never")).tag("never")
                    Text(L10n.t("When unavailable")).tag("when_unavailable")
                    Text(L10n.t("Allowed within cap")).tag("allowed_within_cap")
                }
                .help("Controls whether routing may leave subscription or proven-zero routes.")
                laneStatus(.paidFallback)
            }
            KeyValueRow(key: L10n.t("Quality tiers"), value: "\(qualityTierCount()) configured")
            HStack {
                Picker(L10n.t("Primary harness"), selection: primaryHarnessBinding()) {
                    Text(L10n.t("None")).tag("__none")
                    ForEach(model.selectableHarnesses.filter { $0 != .raw }) { family in
                        Label {
                            Text(family.label)
                        } icon: {
                            HarnessIconImage.image(for: family)
                        }
                        .tag(family.rawValue)
                    }
                }
                .help("Primary is a bias, not a hardcoded semantic role.")
                laneStatus(.primaryHarness)
            }
            HStack {
                Picker(
                    L10n.t("Env inheritance"),
                    selection: draftBinding(\.envInheritance, lane: .envInheritance)
                ) {
                    Text(L10n.t("Mirror native")).tag("mirror_native")
                    Text(L10n.t("Clean")).tag("clean")
                }
                .help("mirror_native reuses native CLI auth/session context by default.")
                laneStatus(.envInheritance)
            }
            HStack {
                Picker(
                    L10n.t("Auth route"),
                    selection: draftBinding(\.authPreference, lane: .authPreference)
                ) {
                    Text(L10n.t("Auto (subscription first)")).tag("auto")
                    Text(L10n.t(LocalizedPresentation.text("Subscription"))).tag("subscription")
                    Text(L10n.t(LocalizedPresentation.text("API key"))).tag("api_key")
                }
                .help("Which credential route harness runs prefer. Auto seeds the native subscription session and falls back to a stored API key; an explicit route discloses any fallback in the run events.")
                laneStatus(.authPreference)
            }
            FlowLayout(spacing: Theme.Spacing.sm) {
                ForEach(model.selectableHarnesses.filter { $0 != .raw }) { family in
                    FilterChip(
                        label: family.label,
                        iconImage: HarnessIconImage.image(for: family),
                        isActive: activeDraft.eligibleHarnesses.contains(family),
                        tint: family.color
                    ) {
                        toggleEligibleHarness(family)
                    }
                    .help("Default eligible pool. Empty means auto-discover available harnesses.")
                }
            }
            laneStatus(.eligibleHarnesses)
            if activeDraft.routingGoal == "quality", qualityTierCount() == 0 {
                Label(
                    "Quality routing has no configured tiers, so this edit is not saved. Add a quality tier with claudexor settings or choose Auto/Economy.",
                    systemImage: "exclamationmark.triangle.fill"
                )
                .font(.caption)
                .foregroundStyle(Theme.status(.caution))
            }
        }
    }

    @ViewBuilder var harnessDoctorGroup: some View {
        settingsGroup(L10n.t("Harness Doctor & Auth"), "cpu") {
            Text(L10n.t("Claudexor mirrors native harness auth first, with API-key fallback through stored secret refs."))
                .font(.caption)
                .foregroundStyle(.secondary)
            if case .failed(let message) = model.activeAccountsLoadState {
                VStack(alignment: .leading, spacing: Theme.Spacing.xs) {
                    Label(LocalizedPresentation.text(LocalizedPresentation.text("Could not refresh accounts and readiness")),
                          systemImage: "exclamationmark.triangle.fill")
                        .font(.caption.weight(.medium))
                        .foregroundStyle(Theme.status(.negative))
                    Text(message).font(.caption2).foregroundStyle(.secondary)
                    Button(L10n.t("Retry")) { Task { _ = await model.refreshAccounts() } }
                        .buttonStyle(.bordered).controlSize(.small)
                }
            }
            KeyValueRow(
                key: "Control API",
                value: model.endpoint.isEmpty ? "—" : "http://\(model.endpoint)",
                mono: true
            )
            GitReadinessCard(
                capability: model.activeGitCapability,
                readinessFresh: model.activeHarnessReadinessFresh
            )
            ForEach(model.selectableHarnesses.filter { $0 != .raw }) { family in
                nativeAuthRow(family)
            }
        }
    }

    @ViewBuilder var secretsGroup: some View {
        settingsGroup(L10n.t("Secrets"), "key") {
            Text(L10n.t("Secret values live in the v2 0600 file store. Run params and artifacts store refs/metadata only."))
                .font(.caption)
                .foregroundStyle(.secondary)
            KeyValueRow(key: L10n.t("Secret backend"), value: model.activeSecretBackend)
            if !model.activeStoredSecrets.isEmpty {
                FlowLayout(spacing: Theme.Spacing.xs) {
                    ForEach(model.activeStoredSecrets) { secret in
                        Text("\(secret.name) · \(secret.backend)")
                            .font(.caption2)
                            .padding(.horizontal, Theme.Spacing.sm)
                            .padding(.vertical, 2)
                            .background(Theme.surfaceRaisedHi, in: Capsule())
                            .foregroundStyle(.secondary)
                    }
                }
            }
            FlowLayout(spacing: Theme.Spacing.sm) {
                ForEach(model.selectableHarnesses) { family in
                    Button {
                        model.authSheetTarget = AuthSheetTarget(family: family)
                    } label: {
                        Label {
                            Text("Open \(family.label) Auth")
                        } icon: {
                            HarnessIconImage.image(for: family)
                        }
                    }
                    .buttonStyle(.bordered)
                    .help("Store fallback refs and run setup jobs in the shared \(family.label) Auth sheet.")
                }
            }
        }
    }

    @ViewBuilder var perHarnessGroup: some View {
        settingsGroup(L10n.t("Per-Harness Defaults"), "slider.horizontal.3") {
            Text(L10n.t("Engine-level defaults per harness: enable/disable, model override, effort, and web policy. Stored in ~/.claudexor/v3/config.yaml."))
                .font(.caption)
                .foregroundStyle(.secondary)
            ForEach(model.selectableHarnesses.filter { $0 != .raw }) { family in
                HarnessDefaultsRow(
                    family: family,
                    settings: model.activeSettingsSnapshot?.harnesses?[family.rawValue],
                    autosave: $harnessAutosave
                )
            }
        }
    }
}
