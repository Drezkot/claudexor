#!/usr/bin/env python3

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/macos/ClaudexorApp/Sources/ClaudexorApp"


def patch(name, replacements):
    p = APP / name
    if not p.exists():
        print("missing:", name)
        return 0

    s = p.read_text()
    old = s

    for src, dst in replacements:
        s = s.replace(src, dst)

    if s != old:
        p.write_text(s)
        print("patched:", name)
        return 1

    return 0


changed = 0

changed += patch("DomainModels.swift", [
    ('return "Connecting"', 'return LocalizedPresentation.text("Connecting")'),
    ('return "Connected"', 'return LocalizedPresentation.text("Connected")'),
    ('return "Offline"', 'return LocalizedPresentation.text("Offline")'),

    ('return "Queued"', 'return LocalizedPresentation.text("Queued")'),
    ('return "Working"', 'return LocalizedPresentation.text("Working")'),
    ('return "Done"', 'return LocalizedPresentation.text("Done")'),
    ('return "Failed"', 'return LocalizedPresentation.text("Failed")'),
    ('return "Cancelled"', 'return LocalizedPresentation.text("Cancelled")'),
    ('return "Interrupted"', 'return LocalizedPresentation.text("Interrupted")'),
    ('return "Unknown"', 'return LocalizedPresentation.text("Unknown")'),

    ('return "Harness failed"', 'return LocalizedPresentation.text("Harness failed")'),
    ('return "No changes"', 'return LocalizedPresentation.text("No changes")'),
    ('return "Review blocked"', 'return LocalizedPresentation.text("Review blocked")'),
    ('return "Checks failed"', 'return LocalizedPresentation.text("Checks failed")'),
    ('return "Exhausted"', 'return LocalizedPresentation.text("Exhausted")'),
    ('return "Budget overshot"', 'return LocalizedPresentation.text("Budget overshot")'),
    ('return "Cost unverifiable"', 'return LocalizedPresentation.text("Cost unverifiable")'),
    ('return "Not converged"', 'return LocalizedPresentation.text("Not converged")'),
    ('return "Stuck/no progress"', 'return LocalizedPresentation.text("Stuck/no progress")'),
    ('return "Workspace unavailable"', 'return LocalizedPresentation.text("Workspace unavailable")'),
    ('return "Time limit reached"', 'return LocalizedPresentation.text("Time limit reached")'),

    ('return "Best-of-N"', 'return LocalizedPresentation.text("Best-of-N")'),
    ('return "Max Attempts"', 'return LocalizedPresentation.text("Max Attempts")'),
    ('return "Until Clean"', 'return LocalizedPresentation.text("Until Clean")'),
    ('return "Create"', 'return LocalizedPresentation.text("Create")'),
    ('return "Read-only Audit"', 'return LocalizedPresentation.text("Read-only Audit")'),
    ('return "Unknown Mode"', 'return LocalizedPresentation.text("Unknown Mode")'),

    ('return "Reviewing"', 'return LocalizedPresentation.text("Reviewing")'),
    ('return "Clean"', 'return LocalizedPresentation.text("Clean")'),
    ('return "Changes requested"', 'return LocalizedPresentation.text("Changes requested")'),
    ('return "Winner"', 'return LocalizedPresentation.text("Winner")'),
    ('return "Rejected"', 'return LocalizedPresentation.text("Rejected")'),
])

changed += patch("WorkspaceTabs.swift", [
    ('return "Changes"', 'return LocalizedPresentation.text("Changes")'),
    ('return "Artifacts"', 'return LocalizedPresentation.text("Artifacts")'),
    ('return "Evidence"', 'return LocalizedPresentation.text("Evidence")'),
    ('return "Terminal"', 'return LocalizedPresentation.text("Terminal")'),

    ('case .changes: "Changes"', 'case .changes: LocalizedPresentation.text("Changes")'),
    ('case .artifacts: "Artifacts"', 'case .artifacts: LocalizedPresentation.text("Artifacts")'),
    ('case .evidence: "Evidence"', 'case .evidence: LocalizedPresentation.text("Evidence")'),
    ('case .terminal: "Terminal"', 'case .terminal: LocalizedPresentation.text("Terminal")'),
])

changed += patch("AccessProfile.swift", [
    ('return "Read-only"', 'return LocalizedPresentation.text("Read-only")'),
    ('return "Workspace write"', 'return LocalizedPresentation.text("Workspace write")'),
    ('return "Full access"', 'return LocalizedPresentation.text("Full access")'),
    ('return "Inherit native"', 'return LocalizedPresentation.text("Inherit native")'),

    ('case .readonly: "Read-only"', 'case .readonly: LocalizedPresentation.text("Read-only")'),
    ('case .workspaceWrite: "Workspace write"', 'case .workspaceWrite: LocalizedPresentation.text("Workspace write")'),
    ('case .full: "Full access"', 'case .full: LocalizedPresentation.text("Full access")'),
    ('case .inheritNative: "Inherit native"', 'case .inheritNative: LocalizedPresentation.text("Inherit native")'),
])

changed += patch("ComposerStrategy.swift", [
    ('return "Single"', 'return "Один агент"'),
    ('return "Best-of"', 'return "Лучший из вариантов"'),
    ('return "Until clean"', 'return "До чистого результата"'),
    ('return "Create"', 'return "Создать"'),

    ('case .single: "Single"', 'case .single: "Один агент"'),
    ('case .bestOf: "Best-of"', 'case .bestOf: "Лучший из вариантов"'),
    ('case .untilClean: "Until clean"', 'case .untilClean: "До чистого результата"'),
    ('case .create: "Create"', 'case .create: "Создать"'),
])

changed += patch("RemoteConnectionSettingsViews.swift", [
    ('case .offline: "Offline"',
     'case .offline: LocalizedPresentation.text("Offline")'),
    ('case .connecting: "Connecting"',
     'case .connecting: LocalizedPresentation.text("Connecting")'),
    ('case .needsInteraction: "Needs authentication"',
     'case .needsInteraction: "Требуется авторизация"'),
    ('case .installing: "Installing"',
     'case .installing: "Установка"'),
    ('case .connected: "Connected"',
     'case .connected: LocalizedPresentation.text("Connected")'),
    ('case .failed: "Failed"',
     'case .failed: LocalizedPresentation.text("Failed")'),
])

changed += patch("ReviewFindingModels.swift", [
    ('return "Proposed"', 'return LocalizedPresentation.text("Proposed")'),
    ('return "Accepted"', 'return LocalizedPresentation.text("Accepted")'),
    ('return "Rebutted"', 'return LocalizedPresentation.text("Rebutted")'),
    ('return "Fixed"', 'return LocalizedPresentation.text("Fixed")'),
    ('return "Accepted Risk"', 'return LocalizedPresentation.text("Accepted Risk")'),
    ('return "Duplicate"', 'return LocalizedPresentation.text("Duplicate")'),
    ('return "Stale"', 'return LocalizedPresentation.text("Stale")'),
    ('return "Out of Scope"', 'return LocalizedPresentation.text("Out of Scope")'),
    ('return "Insufficient"', 'return LocalizedPresentation.text("Insufficient")'),
    ('return "Not reviewed"', 'return LocalizedPresentation.text("Not reviewed")'),
    ('return "Running"', 'return LocalizedPresentation.text("Running")'),
    ('return "Clean"', 'return LocalizedPresentation.text("Clean")'),
    ('return "Findings"', 'return LocalizedPresentation.text("Findings")'),
    ('return "Failed"', 'return LocalizedPresentation.text("Failed")'),
    ('return "Error"', 'return LocalizedPresentation.text("Error")'),
])

print()
print(f"Pass 9 complete. Changed files: {changed}")
