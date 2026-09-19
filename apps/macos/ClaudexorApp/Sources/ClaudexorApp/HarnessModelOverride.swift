import SwiftUI
import ClaudexorKit

/// Model override control for one harness row (ADP4). A Picker over the
/// harness's model TRUTH SOURCE (live inventory or manifest known-good
/// hints). STRICT: there is no free-text entry — a harness with no
/// truth source runs its default only, and a model outside the source would
/// be refused by the engine anyway. The view owns catalog loading so a
/// transport failure is distinguishable from an ANSWERED "no truth source".
@MainActor
struct HarnessModelOverrideField: View {
    let family: HarnessFamily
    @Binding var modelDraft: String
    /// One-shot enumeration; thin consumer of the control-api DTO. nil =
    /// offline/failed, so the neutral catalog-unavailable state renders.
    let fetch: (HarnessFamily) async -> HarnessModelsResponse?
    /// Owned by the row (the save path derives modelEditable from it); the
    /// subview only loads and renders through this binding.
    @Binding var models: HarnessModelsResponse?

    @State private var loadingModels = false
    /// True when the LAST fetch returned nil (offline/failed) — distinct from
    /// "not yet loaded" and from an answered source:"none".
    @State private var loadFailed = false

    var body: some View {
        content.task { await loadModels() }
    }

    @ViewBuilder private var content: some View {
        switch modelFieldState(models: models, modelDraft: modelDraft, loadFailed: loadFailed) {
        case .picker:
            picker
        case .refusedLegacy:
            refusedLegacy
        case .unavailableWithDraft:
            unavailableWithDraft
        case .unavailable:
            unavailableNoDraft
        case .defaultOnly:
            LabeledContent("Model") {
                Text(L10n.t("Harness default only"))
                    .font(.caption).foregroundStyle(.secondary)
            }
            .help(modelFallbackHelp)
        case .loading:
            // Catalog not answered yet: a transient state, not a truth claim.
            LabeledContent("Model") {
                Text(L10n.t("Loading model catalog…"))
                    .font(.caption).foregroundStyle(.secondary)
            }
            .help("Загрузка каталога моделей \(family.label)…")
        }
    }

    /// Same `LabeledContent("Model")` shell as every sibling state above, so
    /// the row does not re-layout when the catalog resolves; the control obeys
    /// the shared catalog-picker contract (fixed token width + capped menu
    /// titles) exactly like the composer surface.
    @ViewBuilder private var picker: some View {
        if let models {
            LabeledContent("Model") {
                Picker(L10n.t("Model override"), selection: $modelDraft) {
                    Text(L10n.t("Harness default")).tag("")
                    // A stored override the truth source no longer lists (legacy
                    // value) stays visible so the user can SEE and clear it — the
                    // engine refuses it at run preflight either way. Rendered
                    // through the shared cap so a pathological stored id cannot
                    // widen the open menu (the tag keeps the FULL id).
                    if !modelDraft.isEmpty, !models.models.contains(where: { $0.id == modelDraft }) {
                        Text("\(HarnessModelPresentation.menuTitle(label: nil, id: modelDraft)) (нет в списке \(models.source))")
                            .tag(modelDraft)
                    }
                    ForEach(models.models) { m in
                        Text(HarnessModelPresentation.menuTitle(label: m.label, id: m.id)).tag(m.id)
                    }
                }
                .catalogModelPicker()
            }
            .help(modelPickerHelp(models))
        }
    }

    /// The harness ANSWERED with no truth source: a stored legacy override
    /// will be refused at preflight, so SHOW it and offer the only
    /// meaningful action — clearing it (explicit null on save).
    private var refusedLegacy: some View {
        LabeledContent("Model") {
                HStack(spacing: Theme.Spacing.xs) {
                    Text("\(modelDraft) — отклонено (нет источника данных)")
                        .font(.caption).foregroundStyle(.orange)
                    Button(L10n.t("Clear")) { modelDraft = "" }
                        .controlSize(.small)
                        .help("Removes the stored override so this harness runs its default model.")
                }
            }
            .help(modelFallbackHelp)
    }

    /// Catalog request failed (engine offline / transient): do NOT claim the
    /// override is refused — we could not check it. Retry refetches.
    private var unavailableWithDraft: some View {
        LabeledContent("Model") {
                HStack(spacing: Theme.Spacing.xs) {
                    Text("\(modelDraft) — каталог моделей недоступен")
                        .font(.caption).foregroundStyle(.secondary)
                    Button(L10n.t("Retry")) { Task { await loadModels(force: true) } }
                        .controlSize(.small)
                        .help("Обновите каталог моделей \(family.label), чтобы проверить это переопределение.")
                }
            }
            .help("Не удалось загрузить каталог моделей \(family.label); переопределение сохранено без изменений. После переподключения повторите проверку.")
    }

    /// Catalog fetch failed with no stored override: offer Retry and do NOT
    /// claim the harness has no truth source — we don't know yet.
    private var unavailableNoDraft: some View {
        LabeledContent("Model") {
                HStack(spacing: Theme.Spacing.xs) {
                    Text(L10n.t("Model catalog unavailable"))
                        .font(.caption).foregroundStyle(.secondary)
                    Button(L10n.t("Retry")) { Task { await loadModels(force: true) } }
                        .controlSize(.small)
                        .help("Обновить каталог моделей \(family.label).")
                }
            }
            .help("Не удалось загрузить каталог моделей \(family.label). Переподключитесь и повторите попытку.")
    }

    private func modelPickerHelp(_ models: HarnessModelsResponse) -> String {
        let freshness = models.verifiedAgainst.map { " (проверено через CLI \($0))" } ?? ""
        return "Модель передана \(family.label); источник: \(models.source)\(freshness). Значение по умолчанию оставляет выбор движку."
    }

    private var modelFallbackHelp: String {
        if loadingModels { return "Загрузка моделей \(family.label)…" }
        return "\(family.label) не предоставляет источник списка моделей, поэтому используется модель по умолчанию; явное указание модели будет отклонено."
    }

    private func loadModels(force: Bool = false) async {
        if force { models = nil }
        guard models == nil, !loadingModels else { return }
        loadingModels = true
        loadFailed = false
        defer { loadingModels = false }
        models = await fetch(family)
        loadFailed = models == nil
    }
}
