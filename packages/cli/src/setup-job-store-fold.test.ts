import { mkdtempSync, realpathSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { journalFoldPolicy } from "@claudexor/daemon";
import type { DurableJournal, JournalFold, JournalRecord } from "@claudexor/journal";
import type { ControlSetupJob } from "@claudexor/schema";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { SetupJobStore } from "./setup-job-store.js";

let root: string;
beforeEach(() => {
  root = realpathSync(mkdtempSync(join(tmpdir(), "setup-store-fold-")));
});
afterEach(() => {
  rmSync(root, { recursive: true, force: true });
});

const job = (jobId: string): ControlSetupJob => ({
  jobId,
  harness: "codex",
  action: "login",
  transport: "daemon",
  state: "queued",
  phase: "preparing",
  command: null,
  guideUrl: null,
  message: "waiting",
  createdAt: "2026-01-01T00:00:00.000Z",
  startedAt: null,
  finishedAt: null,
  profileId: null,
  authCapability: {
    attemptId: `attempt-${jobId}`,
    challengeDigest: "a".repeat(64),
    requestDigest: "b".repeat(64),
    disclosure: {
      schemaVersion: 1,
      protocolVersion: 1,
      harness: "codex",
      requested: "subscription",
      requiredRoute: "vendor_native",
      requiredSource: "native_session",
      networkScope: "selected_harness_only",
      billingKnowledge: "unknown",
      incrementalCostKnowledge: "unknown",
      mayConsumeQuota: true,
      generatedAt: "2026-01-01T00:00:00.000Z",
    },
    state: "disclosed",
  },
});

/** Mirror of the journal package's `foldStream` semantics (see the daemon's
 * fold-policy test): retire first, slot supersede, then drop-or-register. */
function applyFold(records: readonly JournalRecord[], fold: JournalFold): JournalRecord[] {
  const held = new Map<number, { record: JournalRecord; slot?: string; group?: string }>();
  const slots = new Map<string, number>();
  const groups = new Map<string, Set<number>>();
  let next = 0;
  const drop = (id: number): void => {
    const entry = held.get(id);
    if (!entry) return;
    held.delete(id);
    if (entry.slot !== undefined && slots.get(entry.slot) === id) slots.delete(entry.slot);
    if (entry.group !== undefined) groups.get(entry.group)?.delete(id);
  };
  for (const record of records) {
    const verdict = fold.verdict({
      seq: record.seq,
      type: record.type,
      time: record.time,
      payload: record.payload,
      byteLength: Buffer.byteLength(JSON.stringify(record.payload ?? null)),
    });
    for (const name of verdict.retire ?? []) {
      const holder = slots.get(name);
      if (holder !== undefined) drop(holder);
      for (const id of [...(groups.get(name) ?? [])]) drop(id);
    }
    if (verdict.slot !== undefined) {
      const holder = slots.get(verdict.slot);
      if (holder !== undefined) drop(holder);
    }
    if (verdict.drop) continue;
    const id = next;
    next += 1;
    held.set(id, { record, slot: verdict.slot, group: verdict.group });
    if (verdict.slot !== undefined) slots.set(verdict.slot, id);
    if (verdict.group !== undefined) {
      const members = groups.get(verdict.group) ?? new Set<number>();
      members.add(id);
      groups.set(verdict.group, members);
    }
  }
  return [...held.values()].map((entry) => entry.record);
}

/** Read-only journal view over a retained record list with the disk chain state. */
function listJournal(entries: readonly JournalRecord[], nextSeq: number): DurableJournal {
  const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;
  const view = {
    options: { partition: "global", rootDir: "" },
    records: (afterSeq = 0, types?: readonly string[]) =>
      entries
        .filter((record) => record.seq > afterSeq && (!types || types.includes(record.type)))
        .map((record) => ({ ...record, payload: clone(record.payload) })),
    state: () => ({ status: "ready" as const, discardedTailBytes: 0 }),
    currentSequence: () => nextSeq - 1,
    currentCursor: () => `global:epoch:${nextSeq - 1}`,
    cursorFor: (record: Pick<JournalRecord, "seq">) => `global:epoch:${record.seq}`,
    sequenceAfter: (cursor: string | null | undefined) =>
      cursor ? Number(cursor.split(":").at(-1)) : 0,
  };
  return view as unknown as DurableJournal;
}

describe("journal fold policy over the setup lifecycle projection", () => {
  it("keeps every saved transition (the reducer validates them) and forgets terminal logs", () => {
    const store = new SetupJobStore(root);
    const idempotency = { key: "create-a", client: "test", request: { harness: "codex" } };
    store.create(job("setup-a"), idempotency);
    store.appendLog("setup-a", "launching");
    store.update("setup-a", {
      state: "waiting_for_input",
      message: "awaiting",
      phase: "launching",
      startedAt: "2026-01-01T00:00:01.000Z",
    });
    store.appendLog("setup-a", "still going");
    store.update("setup-a", {
      state: "failed",
      phase: "completed",
      finishedAt: "2026-01-01T00:00:02.000Z",
      outcome: { reason: "launch_failed" },
    });
    store.appendLog("setup-a", "after terminal");
    store.create(job("setup-b"));
    store.appendLog("setup-b", "active job log");
    const full = store.journal.records();
    const nextSeq = store.journal.currentSequence() + 1;
    store.journal.close();

    const folded = applyFold(full, journalFoldPolicy());
    const types = (type: string) => folded.filter((record) => record.type === type);
    expect(types("setup.job.saved")).toHaveLength(
      full.filter((r) => r.type === "setup.job.saved").length,
    );
    expect(types("setup.job.create_bound")).toEqual(
      full.filter((r) => r.type === "setup.job.create_bound"),
    );
    expect(
      types("setup.job.log").map((record) => (record.payload as { line: string }).line),
    ).toEqual([
      expect.stringContaining("after terminal"),
      expect.stringContaining("active job log"),
    ]);

    const replayFull = new SetupJobStore(root, { journal: listJournal(full, nextSeq) });
    const replayFolded = new SetupJobStore(root, { journal: listJournal(folded, nextSeq) });
    for (const replay of [replayFull, replayFolded])
      expect(replay.recoveryState().status).toBe("ready");
    expect(replayFolded.list()).toEqual(replayFull.list());
    expect(replayFolded.status("setup-a")).toEqual(replayFull.status("setup-a"));
    expect(replayFolded.resolveCreate(idempotency)).toEqual(replayFull.resolveCreate(idempotency));
    expect(replayFolded.events("setup-a")).toEqual(replayFull.events("setup-a"));
    expect(replayFolded.events("setup-b")).toEqual(replayFull.events("setup-b"));
    expect(replayFolded.snapshot("setup-b")).toEqual(replayFull.snapshot("setup-b"));
  });
});
