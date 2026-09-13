import type { JobRecord } from "./server.js";
import { isModelOperation } from "@claudexor/schema";

export function productCommandRecords(records: readonly JobRecord[]): JobRecord[] {
  return records.filter(
    ({ id, params }) => !id.startsWith("delivery-") && !isModelOperation(params),
  );
}

/** A terminal run that still needs a human decision: its lifecycle SUCCEEDED
 * but the arbitrated facts are review-blocked or checks-failed. These carry the
 * same operator obligation the old coarse `blocked` job state did, so they must
 * survive age/cap pruning (otherwise the operator loses the run they need to
 * accept-risk / rerun before its evidence is gone). */
function isNeedsDecision(record: JobRecord): boolean {
  const result = record.result as { facts?: { review?: unknown; checks?: unknown } } | null;
  const facts = result && typeof result === "object" ? result.facts : undefined;
  if (!facts || typeof facts !== "object") return false;
  return facts.review === "blocked" || facts.checks === "failed";
}

/** Cap on the serialized `params` bytes retained across terminal product
 * commands (journal sprint owner decision D3, release 1). Prompts stay inline
 * in the command journal, so once their sum passes this bound the OLDEST
 * terminal product commands are pruned regardless of age; the 500/30-day rule
 * is unchanged. Model-operation receipts and needs-decision runs are exempt. */
export const MAX_RETAINED_COMMAND_PARAMS_BYTES = 256 * 1024 * 1024;

/** Select only expired terminal records (D8: job state is the lifecycle;
 * non-terminal = queued/running). Needs-decision (review-blocked / checks-
 * failed) runs are EXEMPT — they keep operator visibility parity with the old
 * `blocked` retention and are never pruned by age/cap or by the byte budget. */
export function prunableCommandIds(
  records: readonly JobRecord[],
  cap: number,
  retentionMs: number,
  now: number,
  maxParamsBytes = MAX_RETAINED_COMMAND_PARAMS_BYTES,
): string[] {
  // Model bodies have their own custody lifetime. Their compact receipts and
  // idempotency keys survive it, and must not consume Agent history capacity.
  // Delivery commands retain their existing age/cap policy.
  const terminal = records
    .filter(
      (record) => !isModelOperation(record.params) && !["running", "queued"].includes(record.state),
    )
    .sort((a, b) => (a.createdAt < b.createdAt ? -1 : 1));
  const pruned = new Set<string>();
  if (terminal.length > cap) {
    for (const record of terminal
      .filter((record) => {
        if (isNeedsDecision(record)) return false;
        const settledAt = Date.parse(record.finishedAt ?? "");
        return Number.isFinite(settledAt) && now - settledAt >= retentionMs;
      })
      .slice(0, terminal.length - cap)) {
      pruned.add(record.id);
    }
  }
  // Byte budget over what survives the age/cap rule, oldest first.
  let bytes = 0;
  const sizes = new Map<string, number>();
  for (const record of terminal) {
    if (pruned.has(record.id)) continue;
    const size = paramsBytes(record);
    sizes.set(record.id, size);
    bytes += size;
  }
  for (const record of terminal) {
    if (bytes <= maxParamsBytes) break;
    if (pruned.has(record.id) || isNeedsDecision(record)) continue;
    pruned.add(record.id);
    bytes -= sizes.get(record.id) ?? 0;
  }
  return [...pruned];
}

function paramsBytes(record: JobRecord): number {
  try {
    return JSON.stringify(record.params)?.length ?? 0;
  } catch {
    return 0;
  }
}
