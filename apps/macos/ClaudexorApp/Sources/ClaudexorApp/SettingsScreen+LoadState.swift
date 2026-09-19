import SwiftUI

extension SettingsScreen {
    /// Engine-backed editors never materialize defaults as if they were loaded
    /// truth. App-local controls remain usable while this projection retries.
    @ViewBuilder func loadedSettings<Content: View>(
        @ViewBuilder _ content: () -> Content
    ) -> some View {
        switch model.activeSettingsLoadState {
        case .loaded:
            content()
        case .idle, .loading:
            SettingsGroup("Engine settings", systemImage: "arrow.clockwise") {
                HStack(spacing: Theme.Spacing.sm) {
                    ProgressView().controlSize(.small)
                    Text(L10n.t("Loading settings from this engine…"))
                        .font(.caption).foregroundStyle(.secondary)
                }
            }
        case .failed(let message):
            SettingsGroup(
                "Engine settings", systemImage: "exclamationmark.triangle.fill"
            ) {
                Text(message).font(.caption).foregroundStyle(Theme.status(.negative))
                Button(L10n.t("Retry")) { Task { await model.refreshSettings() } }
                    .buttonStyle(.borderedProminent).controlSize(.small)
            }
        }
    }
}
