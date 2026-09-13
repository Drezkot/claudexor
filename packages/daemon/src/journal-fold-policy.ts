/**
 * The daemon's journal fold policy: which retained records a partition may
 * forget at replay and at compaction (journal sprint owner decision D1). The
 * journal package stays generic — it applies these verdicts in seq order — and
 * this module decides WHAT is dead, per record type, from the payload alone.
 *
 * Every verdict is a pure function of the record: no state is carried between
 * records, so one policy object serves read-only preparation, activation and
 * background compaction alike, and the fold can never depend on what a
 * previous pass saw. An unknown or malformed record is always kept — the fold
 * forgets superseded history, never evidence it cannot classify.
 *
 * Invariants the projections replay under (the equivalence test pins them):
 *   - a command keeps its `command.accepted` and its latest `command.updated`;
 *     `command.pruned` forgets both (model-operation receipts are never pruned
 *     by retention, so they survive forever — INV-064);
 *   - a terminal run keeps exactly its terminal `run.event`; a live run keeps
 *     `run.created` plus its journaled progress events;
 *   - a resolved interaction forgets its request AND its resolution as a pair
 *     (a resolution follows its request, so retiring on the resolution can
 *     never leave a partial pair — an `interrupted` or `run_terminal`
 *     resolution lands AFTER the run's terminal event);
 *   - quota keeps the latest projection marker and, per subject key, the
 *     latest scoped prepare and the latest upsert (a pair keeps both members
 *     at their original adjacent seq); `quota.subject.removed` retires every
 *     slot of that (harness, subject_id) across routes and sources;
 *   - `thread.head.updated` keeps the latest revision per thread;
 *   - `setup.job.saved` is kept whole (the setup reducer validates every
 *     state/phase/evidence transition, so intermediate saves are replay
 *     authority); a terminal save retires the job's `setup.job.log` lines.
 */
import type { FoldRecord, FoldVerdict, JournalFold } from "@claudexor/journal";
import {
  CredentialRoute,
  QuotaSnapshot as QuotaSnapshotSchema,
  QuotaSource,
  TERMINAL_CONTROL_SETUP_JOB_STATES,
} from "@claudexor/schema";
import { legacyV320Snapshot, snapshotKey } from "./quota-registry-support.js";

const KEEP: FoldVerdict = Object.freeze({});
const TERMINAL_RUN_EVENTS = new Set(["run.completed", "run.failed", "run.blocked"]);
const TERMINAL_SETUP_STATES = new Set<string>(TERMINAL_CONTROL_SETUP_JOB_STATES);

/** One policy object for every partition (global and project alike). */
export function journalFoldPolicy(): JournalFold {
  return { verdict: journalFoldVerdict };
}

export function journalFoldVerdict(record: FoldRecord): FoldVerdict {
  try {
    switch (record.type) {
      case "command.accepted":
        return slotOrKeep(commandId(record.payload), (id) => `c:${id}:a`);
      case "command.updated":
        return slotOrKeep(commandId(record.payload), (id) => `c:${id}:u`);
      case "command.pruned":
        return prunedVerdict(record.payload);
      case "run.event":
        return runEventVerdict(record.payload);
      case "interaction.requested":
        return interactionRequestedVerdict(record.payload);
      case "interaction.resolved":
        return interactionResolvedVerdict(record.payload);
      case "quota.projection.updated":
        return { slot: "q:marker" };
      case "quota.snapshot.scoped_prepared":
        return slotOrKeep(scopedPreparedKey(record.payload), (key) => `q:${key}:p`);
      case "quota.snapshot.upserted":
        return slotOrKeep(upsertedKey(record.payload), (key) => `q:${key}:u`);
      case "quota.subject.removed":
        return removedSubjectVerdict(record.payload);
      case "thread.head.updated":
        return slotOrKeep(stringField(record.payload, "thread_id"), (id) => `t:${id}`);
      case "setup.job.saved":
        return setupSavedVerdict(record.payload);
      case "setup.job.log":
        return groupOrKeep(stringField(record.payload, "jobId"), (id) => `s:${id}:log`);
      default:
        return KEEP;
    }
  } catch {
    return KEEP;
  }
}

function slotOrKeep(key: string | null, name: (key: string) => string): FoldVerdict {
  return key === null ? KEEP : { slot: name(key) };
}

function groupOrKeep(key: string | null, name: (key: string) => string): FoldVerdict {
  return key === null ? KEEP : { group: name(key) };
}

function object(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function stringField(value: unknown, key: string): string | null {
  const field = object(value)?.[key];
  return typeof field === "string" && field.length > 0 ? field : null;
}

function stringList(value: unknown): string[] | null {
  if (!Array.isArray(value) || value.length === 0) return null;
  return value.every((item) => typeof item === "string" && item.length > 0)
    ? (value as string[])
    : null;
}

function commandId(payload: unknown): string | null {
  return stringField(object(payload)?.record, "id");
}

function prunedVerdict(payload: unknown): FoldVerdict {
  const ids = stringList(object(payload)?.ids);
  if (!ids) return KEEP;
  return { drop: true, retire: ids.flatMap((id) => [`c:${id}:a`, `c:${id}:u`]) };
}

/** A terminal run keeps only its terminal: `run.created` and the journaled
 * progress events are forgotten with it (the macOS app auto-attaches on
 * `run.created` only for live runs; durable terminal recovery reads terminals
 * only; the per-run stream replays `events.jsonl`). */
function runEventVerdict(payload: unknown): FoldVerdict {
  const runId = stringField(payload, "run_id");
  const type = stringField(payload, "type");
  if (runId === null || type === null) return KEEP;
  if (TERMINAL_RUN_EVENTS.has(type)) {
    return { slot: `r:${runId}:t`, retire: [`r:${runId}:live`, `r:${runId}:c`] };
  }
  if (type === "run.created") return { slot: `r:${runId}:c` };
  return { group: `r:${runId}:live` };
}

function interactionRequestedVerdict(payload: unknown): FoldVerdict {
  const runId = stringField(payload, "runId");
  const interactionId = stringField(payload, "interactionId");
  if (runId === null || interactionId === null) return KEEP;
  return { slot: `i:${runId}:${interactionId}` };
}

/** The resolution retires exactly the requests it settles and is itself
 * forgotten: the InteractionStore rebuilds only still-pending questions. */
function interactionResolvedVerdict(payload: unknown): FoldVerdict {
  const runId = stringField(payload, "runId");
  const interactionIds = stringList(object(payload)?.interactionIds);
  if (runId === null || !interactionIds) return KEEP;
  return { drop: true, retire: interactionIds.map((id) => `i:${runId}:${id}`) };
}

/** Both members of a scoped pair are keyed by the LEGACY base snapshot, which
 * is the key the committing upsert carries on the wire (sources are
 * harness-specific, so the only legacy remap — cursor_rate_limit to
 * claude_api_retry — never collides with a genuine legacy-source snapshot of
 * the same subject). */
function scopedPreparedKey(payload: unknown): string | null {
  const snapshot = QuotaSnapshotSchema.safeParse(object(payload)?.snapshot);
  return snapshot.success ? snapshotKey(legacyV320Snapshot(snapshot.data)) : null;
}

function upsertedKey(payload: unknown): string | null {
  const snapshot = QuotaSnapshotSchema.safeParse(payload);
  return snapshot.success ? snapshotKey(snapshot.data) : null;
}

/** `quota.subject.removed` names only (harness, subject_id); the registry
 * removes every snapshot of that subject across routes and sources, so the
 * retire list enumerates the schema's route and source vocabularies. A journal
 * can only replay sources the schema still knows, so the enumeration is
 * complete for every replayable record. */
function removedSubjectVerdict(payload: unknown): FoldVerdict {
  const value = object(payload);
  const harness = typeof value?.harness === "string" ? value.harness : null;
  const subjectId = value?.subject_id;
  if (harness === null || (typeof subjectId !== "string" && subjectId !== null)) return KEEP;
  const subject = subjectId ?? "";
  const retire: string[] = [];
  for (const route of CredentialRoute.options) {
    for (const source of QuotaSource.options) {
      const key = [harness, route, subject, source].join("\0");
      retire.push(`q:${key}:p`, `q:${key}:u`);
    }
  }
  return { slot: `q:${harness}\0${subject}:removed`, retire };
}

function setupSavedVerdict(payload: unknown): FoldVerdict {
  const job = object(object(payload)?.job);
  const jobId = stringField(job, "jobId");
  const state = stringField(job, "state");
  if (jobId === null || state === null || !TERMINAL_SETUP_STATES.has(state)) return KEEP;
  return { retire: [`s:${jobId}:log`] };
}
