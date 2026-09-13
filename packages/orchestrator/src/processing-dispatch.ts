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
  // A concrete profile on the prepared spec is authoritative. The extra is
  // only a resolver/fallback for routes that have no profile identity yet.
  const profileBilling =
    spec.credential_profile?.credential_kind === "api_key"
      ? "metered"
      : spec.credential_profile
        ? "subscription_entitlement"
        : undefined;
  const resolver = spec.extra["routeBillingKnowledge"];
  const resolved =
    profileBilling ??
    (typeof resolver === "function"
      ? (resolver as (actual: HarnessRunSpec) => unknown)(spec)
      : resolver);
  const ordinary =
    resolved === "metered" || resolved === "subscription_entitlement" || resolved === "unknown"
      ? resolved
      : spec.credential_profile?.credential_kind === "api_key"
        ? "metered"
        : spec.credential_profile
          ? "subscription_entitlement"
          : spec.auth_preference === "api_key"
            ? "metered"
            : spec.auth_preference === "subscription"
              ? "subscription_entitlement"
              : "unknown";
  return processingCostEvidence(
    { model: spec.model_hint, receipt: spec.processing, costBasis: spec.processing_cost_basis },
    ordinary,
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
  spec.extra["markPhysicalDispatchStarted"] = () => ledger.markPhysicalDispatchStarted(leaseId);
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
  let paidOrUnknownSeen = false;
  return (index, spec) => {
    const current = preparedCost(spec, reviewers[index]!.adapter.id);
    if (!current) return;
    costs[index] = current;
    const currentPaid =
      current.billing !== "proven_zero" && current.billing !== "subscription_entitlement";
    paidOrUnknownSeen ||= currentPaid;
    // A later included route must not erase the paid/unknown class already
    // admitted for this panel lease. The marker remains until settle/cancel.
    if (!currentPaid && paidOrUnknownSeen) return;
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
