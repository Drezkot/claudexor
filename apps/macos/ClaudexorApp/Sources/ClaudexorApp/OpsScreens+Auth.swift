import SwiftUI
import ClaudexorKit

extension SettingsScreen {
    /// The one readiness card. Remote locations route login through their SSH
    /// terminal; local locations retain the existing auth sheet.
    func nativeAuthRow(_ family: HarnessFamily) -> some View {
        let presentation = HarnessReadinessPresentation.from(
            family: family, info: model.harnessInfo(for: family))
        // The remote path starts a PROFILE-LESS login — the BOOTSTRAP flow of
        // the unified account model: the engine resolves it onto the
        // `<harness>-default` account row and the setup job reports the
        // resolved profileId (the remote sheet's readiness refresh adopts it).
        // A family with no bootstrap login (agy: every account is a named row)
        // would post a request the daemon must refuse, so the button goes
        // disabled here and names the path that does work — rather than
        // looking live and failing at the server.
        let connectionID = model.activeExecutionLocation.remoteConnectionID
        let remoteHarness = connectionID == nil
            ? nil : SetupHarness(rawValue: family.setupHarnessId)
        let remoteLoginNeedsAccount = remoteHarness != nil
            && !AccountsPresentation.supportsBootstrapLogin(family)
        return HarnessReadinessCard(presentation: presentation) {
            Button {
                if let connectionID, let harness = remoteHarness {
                    Task {
                        await model.startRemoteLogin(
                            connectionID: connectionID, harness: harness)
                    }
                } else {
                    model.authSheetTarget = AuthSheetTarget(family: family)
                }
            } label: {
                Label(
                    presentation.available ? L10n.t("Manage") : L10n.t("Setup"),
                    systemImage: presentation.available
                        ? "slider.horizontal.3"
                        : "person.crop.circle.badge.checkmark")
            }
            .buttonStyle(.bordered)
            .tint(Theme.accent)
            .disabled(remoteLoginNeedsAccount)
            .help(
                remoteLoginNeedsAccount
                    ? "\(family.label) поддерживает вход только в именованный аккаунт. Добавьте или откройте аккаунт \(family.label) в разделе «Аккаунты» для входа на удалённом хосте."
                    : presentation.available
                        ? "Открыть сведения авторизации \(family.label) и управление резервным ключом."
                        : "Открыть настройку и авторизацию \(family.label).")
            Button {
                Task {
                    await model.refreshHarnesses(fresh: true, markStaleOnFailure: true)
                }
            } label: {
                Label(L10n.t("Recheck"), systemImage: "arrow.clockwise")
            }
            .buttonStyle(.bordered)
            .help("Refresh install/auth/capability status after setup.")
        }
    }
}
