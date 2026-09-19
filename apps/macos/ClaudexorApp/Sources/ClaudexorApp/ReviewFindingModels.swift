import Foundation
import SwiftUI

/// Review-findings domain models. Extracted from `DomainModels.swift` (the
/// readability ratchet) — same UI-side projections of the engine's review axes:
/// severity, route-proof provenance, adjudication status, the finding row, and
/// the review verdict. The canonical shapes live in `packages/schema`.

// MARK: - Review findings

enum Severity: String, CaseIterable, Hashable {
    case blocker, major, minor, nit
    var label: String { rawValue.capitalized }
    var glyph: String {
        switch self {
        case .blocker: return "xmark.octagon.fill"
        case .major: return "exclamationmark.triangle.fill"
        case .minor: return "exclamationmark.circle"
        case .nit: return "sparkle"
        }
    }
    var color: Color {
        switch self {
        case .blocker: return Theme.status(.negative)
        case .major: return Theme.status(.caution)
        case .minor: return Theme.status(.info)
        case .nit: return .secondary
        }
    }
    var rank: Int { Self.allCases.firstIndex(of: self) ?? 9 }
}

enum RouteProof: String, Hashable {
    case verified, acceptedModelArg, unverified, sameModelFallback
    var label: String {
        switch self {
        case .verified: return LocalizedPresentation.text("Route verified")
        case .acceptedModelArg: return LocalizedPresentation.text("Model arg accepted")
        case .unverified: return LocalizedPresentation.text("Route unverified")
        case .sameModelFallback: return LocalizedPresentation.text("Same-model fallback")
        }
    }
    var glyph: String {
        switch self {
        case .verified: return "checkmark.shield.fill"
        case .acceptedModelArg: return "checkmark.shield"
        case .unverified: return "shield"
        case .sameModelFallback: return "exclamationmark.shield"
        }
    }
    var color: Color {
        switch self {
        case .verified: return Theme.status(.positive)
        case .acceptedModelArg: return Theme.accent
        case .unverified: return .secondary
        case .sameModelFallback: return Theme.status(.caution)
        }
    }
}

enum FindingStatus: String, Hashable {
    case proposed
    case accepted
    case rebutted
    case fixed
    case acceptedRisk
    case duplicate
    case stale
    case outOfScope
    case insufficientEvidence

    init(api: String?) {
        switch api?.lowercased() {
        case "accepted": self = .accepted
        case "rebutted": self = .rebutted
        case "fixed": self = .fixed
        case "accepted_risk", "accepted-risk": self = .acceptedRisk
        case "duplicate": self = .duplicate
        case "stale": self = .stale
        case "out_of_scope", "out-of-scope": self = .outOfScope
        case "insufficient_evidence", "insufficient-evidence": self = .insufficientEvidence
        default: self = .proposed
        }
    }

    var label: String {
        switch self {
        case .proposed: return LocalizedPresentation.text("Proposed")
        case .accepted: return LocalizedPresentation.text("Accepted")
        case .rebutted: return LocalizedPresentation.text("Rebutted")
        case .fixed: return LocalizedPresentation.text("Fixed")
        case .acceptedRisk: return LocalizedPresentation.text("Accepted Risk")
        case .duplicate: return LocalizedPresentation.text("Duplicate")
        case .stale: return LocalizedPresentation.text("Stale")
        case .outOfScope: return LocalizedPresentation.text("Out of Scope")
        case .insufficientEvidence: return LocalizedPresentation.text("Insufficient")
        }
    }

    var color: Color {
        switch self {
        case .accepted, .fixed: return Theme.status(.positive)
        case .rebutted, .outOfScope: return Theme.status(.negative)
        case .insufficientEvidence, .acceptedRisk: return Theme.status(.caution)
        case .duplicate, .stale, .proposed: return .secondary
        }
    }
}

struct Finding: Identifiable, Hashable {
    let id: String
    var severity: Severity
    var category: String
    var title: String
    var detail: String
    var reviewer: HarnessFamily
    var routeProof: RouteProof
    var evidenceFile: String?
    var evidenceLine: Int?
    var status: FindingStatus = .proposed
    var taskTitle: String = ""
    var hasEvidence: Bool { evidenceFile != nil }
}

enum ReviewVerdict: String, Hashable {
    case notRun = "not_run"
    case running
    case clean
    case findings
    case failed
    case error

    var label: String {
        switch self {
        case .notRun: return LocalizedPresentation.text("Not reviewed")
        case .running: return LocalizedPresentation.text("Running")
        case .clean: return LocalizedPresentation.text("Clean")
        case .findings: return LocalizedPresentation.text("Findings")
        case .failed: return LocalizedPresentation.text("Failed")
        case .error: return LocalizedPresentation.text("Error")
        }
    }
}
