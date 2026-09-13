import type { BudgetLedger } from "@claudexor/budget";
import type { ProcessingAdmission } from "@claudexor/core";
import type { CostEvidence, HarnessRunSpec } from "@claudexor/schema";
import type { ReviewerSpec } from "@claudexor/review";
import type { AttemptUsageCost } from "./attemptUsageCost.js";
import type { BudgetDenial } from "./budgetFailure.js";
import { processingCostEvidence } from "./processing-routing.js";

/** A budget refusal before native dispatch, never an adapter or auth failure. */
export class ProcessingBudgetAdmissionError extends Error {
  readonly retryable = false;
  readonly category = "budget";
  readonly code: BudgetDenial["code"];
  constructor(readonly denial: BudgetDenial) {
    super(denial.reason);
    this.code = denial.code;
    this.name = "ProcessingBudgetAdmissionError";
  }
}

function preparedCost(spec: HarnessRunSpec, harnessId: string): CostEvidence | undefined {
  if (!spec.processing || !spec.processing_cost_basis) return undefined;
  return processingCostEvidence(
    { model: spec.model_hint, receipt: spec.processing, costBasis: spec.processing_cost_basis },
    "unknown",
    [`harness:${harnessId}`, `profile:${spec.credential_profile?.profile_id ?? "default"}`],
  );
}

function reprice(
  ledger: BudgetLedger,
  leaseId: string,
  cost: CostEvidence,
  harnessId: string,
  attemptId: string | null,
  onDenied?: (denial: BudgetDenial) => void,
): void {
  const result = ledger.repriceReservedLease(leaseId, cost);
  if (result.granted) return;
  const denial: BudgetDenial = {
    code: result.denied!,
    reason: result.reason!,
    harnessId,
    attemptId,
  };
  onDenied?.(denial);
  throw new ProcessingBudgetAdmissionError(denial);
}

/** Bind once when the logical lease and spec meet. Copies/retries preserve the
 * callback, which receives each actual prepared profile/model before spawn. */
export function processingAdmissionForLease(
  ledger: BudgetLedger,
  leaseId: string,
  harnessId: string,
  attemptId: string | null,
  onDenied?: (denial: BudgetDenial) => void,
): ProcessingAdmission {
  return (actual) => {
    const cost = preparedCost(actual, harnessId);
    if (cost) reprice(ledger, leaseId, cost, harnessId, attemptId, onDenied);
  };
}

export function bindProcessingAdmission(
  spec: HarnessRunSpec,
  ledger: BudgetLedger,
  leaseId: string,
  harnessId: string,
  attemptId: string | null,
  onDenied?: (denial: BudgetDenial) => void,
  admission?: ProcessingAdmission,
): ProcessingAdmission {
  const bound =
    admission ?? processingAdmissionForLease(ledger, leaseId, harnessId, attemptId, onDenied);
  spec.extra["processingAdmission"] = bound;
  return bound;
}

/** One panel owns one lease. A later slot must not erase another slot's paid
 * prospective class; observed panel hold/debt stays in the same ledger. */
export function reviewerProcessingAdmission(
  ledger: BudgetLedger,
  leaseId: string,
  reviewers: ReviewerSpec[],
  attemptId: string | null,
  onDenied?: (denial: BudgetDenial) => void,
): (index: number, spec: HarnessRunSpec) => void {
  const costs = reviewers.map((reviewer) =>
    processingCostEvidence(reviewer.processing, "unknown", [`harness:${reviewer.adapter.id}`]),
  );
  return (index, spec) => {
    costs[index] = preparedCost(spec, reviewers[index]!.adapter.id);
    if (!costs.some(Boolean)) return;
    const included = costs.every(
      (cost) => cost?.billing === "subscription_entitlement" || cost?.billing === "proven_zero",
    );
    const cost: CostEvidence = {
      billing: included
        ? "subscription_entitlement"
        : costs.some((c) => c?.billing === "metered")
          ? "metered"
          : "unknown",
      knowledge: included ? "exact" : "unknown",
      estimatedUsd: null,
      source: "review-processing-dispatch",
      provenance: costs.flatMap((c) => c?.provenance ?? ["processing:unknown"]),
    };
    reprice(ledger, leaseId, cost, "review-panel", attemptId, onDenied);
  };
}

/** Streamed amounts share the same lease as admission. Included subscription
 * valuation never becomes a paid hold; unresolved potentially paid amounts do. */
export function updateProcessingStreamHold(
  spec: HarnessRunSpec,
  usage: AttemptUsageCost,
  ledger: BudgetLedger,
  leaseId: string,
  harnessId: string,
  attemptId: string,
): BudgetDenial | null {
  if (!spec.processing) return null;
  const amount = usage.cashUsd + (usage.unknownPaidUsd ?? usage.unknownUsd);
  if (!(amount > 0)) return null;
  ledger.updateHold(leaseId, amount);
  return ledger.tier() === "hard"
    ? {
        code: "hard_cap",
        reason: "The paid budget cap was reached during processing",
        harnessId,
        attemptId,
      }
    : null;
}
