import SwiftUI
import ClaudexorKit

// MARK: - Review verdict mappers (no raw wire strings in the UI)
//
// Pure label/glyph/color mappers for the review verdict, module-internal free
// functions so the thread workspace (RunOutcomeSection) and any other surface
// map the verdict the same way. Formerly `extension TaskDetailView` methods;
// TaskDetailView was retired with the per-run inspector (D42).

func reviewVerdictText(_ verdict: ReviewVerdict) -> String {
    switch verdict {
    case .clean: return LocalizedPresentation.text("Verified final review clean.")
    case .findings: return LocalizedPresentation.text("Review produced findings.")
    case .running: return LocalizedPresentation.text("Review is running.")
    case .failed: return LocalizedPresentation.text("Review failed.")
    case .error: return LocalizedPresentation.text("Review ended with an error.")
    case .notRun: return LocalizedPresentation.text("Not reviewed.")
    }
}

func reviewVerdictGlyph(_ verdict: ReviewVerdict) -> String {
    switch verdict {
    case .clean: return "checkmark.seal.fill"
    case .findings: return "exclamationmark.bubble.fill"
    case .running: return "circle.dotted"
    case .failed, .error: return "xmark.octagon.fill"
    case .notRun: return "person.2.slash"
    }
}

func reviewVerdictColor(_ verdict: ReviewVerdict) -> Color {
    switch verdict {
    case .clean: return Theme.status(.positive)
    case .findings: return Theme.status(.caution)
    case .running: return Theme.status(.info)
    case .failed, .error: return Theme.status(.negative)
    case .notRun: return .secondary
    }
}
