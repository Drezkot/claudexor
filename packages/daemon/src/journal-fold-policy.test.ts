import { mkdirSync, mkdtempSync, realpathSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  DurableJournal,
  type FoldRecord,
  type JournalFold,
  type JournalRecord,
} from "@claudexor/journal";
import { CredentialRoute, QuotaSource, type RunEvent } from "@claudexor/schema";
import { afterEach, describe, expect, it } from "vitest";
import { CommandStore } from "./command-store.js";
import { InteractionStore } from "./interactions.js";
import { journalFoldPolicy, journalFoldVerdict } from "./journal-fold-policy.js";
import { journaledRunEventCopy } from "./journaled-run-events.js";
import { OperatorDecisionStore } from "./operator-decisions.js";
import { ProjectStore } from "./projects.js";
import { QuotaRegistry } from "./quota-registry.js";
import { RunEventStore } from "./run-events.js";
import { ThreadHeadPingEmitter } from "./thread-head-ping.js";
import { ThreadStore } from "./threads.js";

const roots: string[] = [];
afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

function view(type: string, payload: unknown, seq = 1): FoldRecord {
  return { seq, type, time: "2026-09-14T00:00:00.000Z", payload, byteLength: 1 };
}

/**
 * Reference implementation of the journal package's `foldStream` semantics
 * (retire first, slot supersede, then drop-or-register). The engine itself is
 * package-internal; this mirror keeps the daemon's equivalence proof local.
 */
function applyFold<T extends { seq: number; type: string; time: string; payload: unknown }>(
  records: readonly T[],
  fold: JournalFold,
): T[] {
  const held = new Map<number, { record: T; slot?: string; group?: string }>();
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

/** A journal view over a fixed retained record list plus the disk chain state
 * (nextSeq from the last frame on disk, never from the last retained record),
 * exactly what a folded replay sees. */
class ListJournal {
  readonly options: { partition: string; rootDir: string };
  private readonly entries: JournalRecord[];
  private nextSeq: number;
  private readonly initialLength: number;
  constructor(partition: string, entries: readonly JournalRecord[], nextSeq: number) {
    this.options = { partition, rootDir: "" };
    this.entries = [...entries];
    this.nextSeq = nextSeq;
    this.initialLength = this.entries.length;
  }
  records<T = unknown>(afterSeq = 0, types?: readonly string[]): JournalRecord<T>[] {
    return this.entries
      .filter((record) => record.seq > afterSeq && (!types || types.includes(record.type)))
      .map((record) => ({ ...record, payload: JSON.parse(JSON.stringify(record.payload)) as T }));
  }
  append<T>(type: string, payload: T): JournalRecord<T> {
    return this.appendBatch([{ type, payload }])[0] as JournalRecord<T>;
  }
  appendBatch(records: readonly { type: string; payload: unknown }[]): JournalRecord[] {
    return records.map(({ type, payload }) => {
      const record: JournalRecord = {
        partition: this.options.partition,
        epoch: "epoch",
        seq: this.nextSeq,
        previousFrameHash: "",
        frameHash: "",
        time: "2026-09-14T00:00:00.000Z",
        type,
        payload: JSON.parse(JSON.stringify(payload)),
        byteOffset: 0,
      };
      this.nextSeq += 1;
      this.entries.push(record);
      return { ...record, payload: JSON.parse(JSON.stringify(record.payload)) };
    });
  }
  cursorFor(record: Pick<JournalRecord, "partition" | "epoch" | "seq">): string {
    return `${record.partition}:${record.epoch}:${record.seq}`;
  }
  cursorAt(seq: number): string {
    return `${this.options.partition}:epoch:${seq}`;
  }
  currentSequence(): number {
    return this.nextSeq - 1;
  }
  currentCursor(): string {
    return this.cursorAt(this.nextSeq - 1);
  }
  sequenceAfter(cursor: string | null | undefined): number {
    return cursor ? Number(cursor.split(":").at(-1)) : 0;
  }
  state() {
    return { status: "ready" as const, discardedTailBytes: 0 };
  }
  appended(): Array<[string, unknown]> {
    return this.entries.slice(this.initialLength).map((record) => [record.type, record.payload]);
  }
  asJournal(): DurableJournal {
    return this as unknown as DurableJournal;
  }
}

const NOW = new Date("2026-09-14T00:05:00.000Z");
const now = () => NOW;
const T0 = "2026-09-14T00:00:00.000Z";

function snapshot(
  harness: string,
  subjectId: string | null,
  usedRatio: number,
  extra: Partial<{ source: string; applies: string[]; observed: string }> = {},
) {
  return {
    subject: {
      harness,
      credential_route: "vendor_native" as const,
      plan_label: null,
      subject_id: subjectId,
    },
    constraints: [
      {
        id: "five_hour",
        label: "5 hour",
        ...(extra.applies ? { applies_to_models: extra.applies } : {}),
        used_ratio: usedRatio,
        window_seconds: 18_000,
        resets_at: null,
        cooldown_until: null,
      },
    ],
    source: (extra.source ?? "claude_oauth_usage") as "claude_oauth_usage",
    observed_at: extra.observed ?? T0,
    freshness: "fresh" as const,
  };
}

function runEvent(
  runId: string,
  type: RunEvent["type"],
  payload: Record<string, unknown> = {},
  seq = 1,
): RunEvent {
  return { seq, ts: T0, run_id: runId, task_id: `task-${runId}`, type, payload };
}

/** Builds a realistic global partition through the real projections. */
function buildFixture() {
  const root = realpathSync.native(mkdtempSync(join(tmpdir(), "claudexor-fold-policy-")));
  roots.push(root);
  const projectRoots = ["p1", "p2", "p2b"].map((name) => {
    const dir = join(root, name);
    mkdirSync(dir);
    return dir;
  });
  const journal = new DurableJournal({ rootDir: join(root, "journal"), partition: "global", now });
  const projects = new ProjectStore(journal);
  const headPing = new ThreadHeadPingEmitter(journal);
  const threads = new ThreadStore(journal, (ping) => headPing.ping(ping));
  const commands = new CommandStore(journal, now);
  const interactions = new InteractionStore(journal);
  const decisions = new OperatorDecisionStore(journal);
  const runEvents = new RunEventStore(journal);
  const quota = new QuotaRegistry(journal, [], now);
  const record = (event: RunEvent) => runEvents.record(journaledRunEventCopy(event));
  const request = (runId: string, interactionId: string) =>
    interactions.request({
      runId,
      taskId: `task-${runId}`,
      attemptId: "a01",
      harnessId: "fake",
      request: { interaction_id: interactionId, source_tool: "AskUserQuestion", questions: [] },
      requestedAt: T0,
      timeoutAt: null,
    });

  // Registry: one kept project, one relinked then unregistered.
  const p1 = projects.register({ root: projectRoots[0]!, idempotencyKey: "reg-1", clientId: "t" });
  const p2 = projects.register({ root: projectRoots[1]!, idempotencyKey: "reg-2", clientId: "t" });
  projects.relink(p2.id, projectRoots[2]!);
  projects.unregister(p2.id);

  // A thread with a turn, session, lane checkpoint and rename (each pings).
  const thread = threads.createThread({ title: "" });
  const turn = threads.createTurn(thread.id, "First prompt of the thread");
  threads.recordSession(thread.id, "codex", "native-1", "gpt-5", null);
  threads.recordLaneCheckpoint(thread.id, "codex", null, turn.id);
  threads.updateThread(thread.id, { title: "Renamed" });

  const params = (prompt: string) => ({
    mode: "agent",
    prompt,
    scope: { kind: "project", root: projectRoots[0]! },
  });
  const commandKeys: Array<{ params: unknown; idempotencyKey: string; clientId: string }> = [];
  const accept = (id: string, value: unknown) => {
    const key = { params: value, idempotencyKey: `key-${id}`, clientId: "t" };
    commandKeys.push(key);
    return commands.accept({ id, ...key }).record;
  };

  // job-a: a full successful run with an answered question and a decision.
  accept("job-a", params("prompt a"));
  commands.update("job-a", {
    state: "running",
    startedAt: T0,
    runId: "run-a",
    taskId: "task-run-a",
  });
  record(runEvent("run-a", "run.created", { mode: "agent", prompt: "prompt a" }, 1));
  request("run-a", "int-1");
  record(runEvent("run-a", "interaction.requested", { interaction_id: "int-1" }, 2));
  interactions.resolve("run-a", "int-1", "answered");
  record(runEvent("run-a", "interaction.answered", { interaction_id: "int-1" }, 3));
  record(runEvent("run-a", "output.ready", { kind: "answer", path: "final/answer.md" }, 4));
  record(runEvent("run-a", "run.completed", { lifecycle: "succeeded" }, 5));
  commands.update("job-a", {
    state: "succeeded",
    result: { lifecycle: "succeeded" },
    finishedAt: T0,
  });
  decisions.record(
    {
      runId: "run-a",
      action: "accept_risk",
      findingIds: ["f-1"],
      acceptedRisks: ["r-1"],
      patchSha256: `sha256:${"a".repeat(64)}`,
      decidedAt: T0,
    },
    { key: "decision-1", client: "t", request: { runId: "run-a" } },
  );

  // job-b: failed run whose question was still pending at the terminal (the
  // run_terminal resolution lands AFTER the terminal event); later pruned.
  accept("job-b", params("prompt b"));
  commands.update("job-b", {
    state: "running",
    startedAt: T0,
    runId: "run-b",
    taskId: "task-run-b",
  });
  record(runEvent("run-b", "run.created", { mode: "agent", prompt: "prompt b" }, 1));
  request("run-b", "int-4");
  record(runEvent("run-b", "interaction.requested", { interaction_id: "int-4" }, 2));
  record(runEvent("run-b", "run.failed", { lifecycle: "failed" }, 3));
  commands.update("job-b", { state: "failed", error: "boom", finishedAt: T0 });
  interactions.resolveRun("run-b", "run_terminal");

  // job-d: succeeded and pruned together with job-b.
  accept("job-d", params("prompt d"));
  commands.update("job-d", {
    state: "running",
    startedAt: T0,
    runId: "run-d",
    taskId: "task-run-d",
  });
  record(runEvent("run-d", "run.created", { mode: "agent", prompt: "prompt d" }, 1));
  record(runEvent("run-d", "run.completed", { lifecycle: "succeeded" }, 2));
  commands.update("job-d", { state: "succeeded", finishedAt: T0 });
  commands.prune(["job-b", "job-d"]);

  // job-m: a model-operation receipt, retained forever.
  accept("job-m", {
    kind: "model",
    request: { resourceId: "res-1", sha256: `sha256:${"b".repeat(64)}`, sizeBytes: 3 },
  });
  commands.update("job-m", { state: "running", startedAt: T0 });
  commands.update("job-m", {
    state: "succeeded",
    result: { lifecycle: "succeeded" },
    finishedAt: T0,
  });

  // job-c: still queued at the crash; run-c live with a pending question.
  accept("job-c", params("prompt c"));
  record(runEvent("run-c", "run.created", { mode: "ask", prompt: "prompt c" }, 1));
  request("run-c", "int-3");
  record(runEvent("run-c", "interaction.requested", { interaction_id: "int-3" }, 2));
  record(runEvent("run-c", "output.ready", { kind: "answer", path: "final/answer.md" }, 3));

  // job-e: the terminal committed but the command update never did (crash).
  accept("job-e", params("prompt e"));
  commands.update("job-e", {
    state: "running",
    startedAt: T0,
    runId: "run-e",
    taskId: "task-run-e",
  });
  record(runEvent("run-e", "run.created", { mode: "agent", prompt: "prompt e" }, 1));
  record(runEvent("run-e", "run.completed", { lifecycle: "succeeded" }, 2));

  // Quota: changes, scoped pairs, a cursor pair, a removal and a re-add, then a
  // raw upsert after the last marker (crash before its marker).
  quota.upsert(snapshot("claude", "work", 0.4));
  quota.upsert(snapshot("claude", "work", 0.5));
  quota.upsert(snapshot("claude", null, 0.3, { applies: ["fable"] }));
  quota.upsert(snapshot("claude", null, 0.6, { applies: ["fable"] }));
  quota.upsert(snapshot("cursor", "cur", 0.1, { source: "cursor_rate_limit" }));
  quota.upsert(snapshot("cursor", "cur", 0.2, { source: "cursor_rate_limit" }));
  quota.upsert(snapshot("codex", "x", 0.2));
  quota.removeSubject("claude", "work");
  quota.upsert(snapshot("claude", "work", 0.7));
  journal.append("quota.snapshot.upserted", snapshot("codex", "x", 0.3));

  headPing.ping({ threadId: thread.id, projectId: null });
  headPing.ping({ threadId: thread.id, projectId: null });
  journal.append("future.unknown", { keep: true });
  journal.append("journal.partition_quarantined", { schemaVersion: 1 });

  const full = journal.records();
  const nextSeq = journal.currentSequence() + 1;
  journal.close();
  return {
    full,
    nextSeq,
    commandKeys,
    runs: ["run-a", "run-b", "run-c", "run-d", "run-e"],
    threadId: thread.id,
    turnId: turn.id,
    projectId: p1.id,
    projectRoot: projectRoots[0]!,
  };
}

function replay(journal: DurableJournal) {
  const commands = new CommandStore(journal, now);
  commands.validateProjection();
  const interactions = new InteractionStore(journal);
  interactions.validateProjection();
  const decisions = new OperatorDecisionStore(journal);
  decisions.validateProjection();
  const runEvents = new RunEventStore(journal);
  runEvents.validateProjection();
  const projects = new ProjectStore(journal);
  projects.validateProjection();
  const quota = new QuotaRegistry(journal, [], now);
  quota.validateProjection();
  const headPing = new ThreadHeadPingEmitter(journal);
  headPing.validateProjection();
  const threads = new ThreadStore(journal);
  threads.validateProjection();
  commands.recoverAfterStartup();
  interactions.recoverAfterStartup();
  quota.recoverAfterStartup();
  return { commands, interactions, decisions, runEvents, projects, quota, headPing, threads };
}

function observe(
  p: ReturnType<typeof replay>,
  f: ReturnType<typeof buildFixture>,
): Record<string, unknown> {
  return {
    commands: p.commands.records().sort((a, b) => a.id.localeCompare(b.id)),
    idempotency: f.commandKeys.map((key) => {
      try {
        return p.commands.find(key)?.id ?? null;
      } catch (error) {
        return String(error);
      }
    }),
    pending: f.runs.map((run) => p.interactions.pendingForRun(run)),
    decisions: f.runs.map((run) => p.decisions.get(run)),
    projects: p.projects.list(),
    projectByRoot: p.projects.findByRoot(f.projectRoot)?.id ?? null,
    // Snapshot ORDER is Map insertion order (a removal plus re-add already
    // reorders it today) and no consumer reads it positionally; compare the set.
    quota: {
      ...p.quota.read(),
      snapshots: [...p.quota.read().snapshots].sort((a, b) =>
        JSON.stringify([a.subject, a.source]).localeCompare(JSON.stringify([b.subject, b.source])),
      ),
    },
    revision: p.headPing.revision(f.threadId),
    threads: p.threads.listThreads(),
    turns: p.threads.turnsFor(f.threadId),
    sessions: p.threads.sessionsForThread(f.threadId),
    checkpoints: p.threads.laneCheckpointsForThread(f.threadId),
    resumeMap: p.threads.resumeMap(f.threadId),
  };
}

describe("journal fold policy verdicts", () => {
  it("keys commands per id and forgets pruned ids as a pair", () => {
    expect(journalFoldVerdict(view("command.accepted", { record: { id: "job-1" } }))).toEqual({
      slot: "c:job-1:a",
    });
    expect(journalFoldVerdict(view("command.updated", { record: { id: "job-1" } }))).toEqual({
      slot: "c:job-1:u",
    });
    expect(journalFoldVerdict(view("command.pruned", { ids: ["job-1", "job-2"] }))).toEqual({
      drop: true,
      retire: ["c:job-1:a", "c:job-1:u", "c:job-2:a", "c:job-2:u"],
    });
    expect(journalFoldVerdict(view("command.pruned", { ids: [] }))).toEqual({});
  });

  it("keeps only the terminal of a finished run and groups live progress", () => {
    for (const type of ["run.completed", "run.failed", "run.blocked"]) {
      expect(journalFoldVerdict(view("run.event", { run_id: "run-1", type }))).toEqual({
        slot: "r:run-1:t",
        retire: ["r:run-1:live", "r:run-1:c"],
      });
    }
    expect(journalFoldVerdict(view("run.event", { run_id: "run-1", type: "run.created" }))).toEqual(
      {
        slot: "r:run-1:c",
      },
    );
    expect(
      journalFoldVerdict(view("run.event", { run_id: "run-1", type: "output.ready" })),
    ).toEqual({
      group: "r:run-1:live",
    });
    expect(journalFoldVerdict(view("run.event", { type: "output.ready" }))).toEqual({});
  });

  it("forgets a resolved interaction pair through its resolution", () => {
    expect(
      journalFoldVerdict(view("interaction.requested", { runId: "run-1", interactionId: "q-1" })),
    ).toEqual({ slot: "i:run-1:q-1" });
    expect(
      journalFoldVerdict(
        view("interaction.resolved", {
          runId: "run-1",
          interactionIds: ["q-1", "q-2"],
          terminal: "run_terminal",
        }),
      ),
    ).toEqual({ drop: true, retire: ["i:run-1:q-1", "i:run-1:q-2"] });
  });

  it("keys quota by the legacy snapshot key and retires a removed subject everywhere", () => {
    expect(journalFoldVerdict(view("quota.projection.updated", {}))).toEqual({ slot: "q:marker" });
    const base = snapshot("claude", "work", 0.4);
    const key = ["claude", "vendor_native", "work", "claude_oauth_usage"].join("\0");
    expect(journalFoldVerdict(view("quota.snapshot.upserted", base))).toEqual({
      slot: `q:${key}:u`,
    });
    const scoped = snapshot("cursor", "cur", 0.1, { source: "cursor_rate_limit" });
    const legacyKey = ["cursor", "vendor_native", "cur", "claude_api_retry"].join("\0");
    expect(
      journalFoldVerdict(
        view("quota.snapshot.scoped_prepared", { version: 1, base_hash: "x", snapshot: scoped }),
      ),
    ).toEqual({ slot: `q:${legacyKey}:p` });
    const removed = journalFoldVerdict(
      view("quota.subject.removed", { harness: "claude", subject_id: null }),
    );
    expect(removed.slot).toBe("q:claude\0:removed");
    expect(removed.retire).toHaveLength(
      CredentialRoute.options.length * QuotaSource.options.length * 2,
    );
    expect(removed.retire).toContain(
      `q:${["claude", "vendor_native", "", "claude_oauth_usage"].join("\0")}:u`,
    );
    expect(journalFoldVerdict(view("quota.snapshot.upserted", { not: "a snapshot" }))).toEqual({});
  });

  it("keeps the latest head ping per thread, keeps setup saves and retires terminal logs", () => {
    expect(journalFoldVerdict(view("thread.head.updated", { thread_id: "th-1" }))).toEqual({
      slot: "t:th-1",
    });
    expect(journalFoldVerdict(view("setup.job.log", { jobId: "setup-1", line: "x" }))).toEqual({
      group: "s:setup-1:log",
    });
    expect(
      journalFoldVerdict(view("setup.job.saved", { job: { jobId: "setup-1", state: "running" } })),
    ).toEqual({});
    expect(
      journalFoldVerdict(
        view("setup.job.saved", { job: { jobId: "setup-1", state: "succeeded" } }),
      ),
    ).toEqual({ retire: ["s:setup-1:log"] });
  });

  it("keeps everything it cannot classify and never throws", () => {
    for (const type of [
      "thread.entities_upserted",
      "project.registered",
      "operator.decision_recorded",
      "journal.recovery_tail_discarded",
      "setup.job.create_bound",
      "future.unknown",
    ]) {
      expect(journalFoldVerdict(view(type, { anything: true }))).toEqual({});
    }
    const hostile = new Proxy(
      {},
      {
        get() {
          throw new Error("poisoned payload");
        },
      },
    );
    expect(journalFoldVerdict(view("command.accepted", hostile))).toEqual({});
    expect(journalFoldVerdict(view("run.event", null))).toEqual({});
    expect(journalFoldPolicy().verdict(view("command.accepted", { record: { id: "x" } }))).toEqual({
      slot: "c:x:a",
    });
  });
});

describe("journal fold policy replay equivalence", () => {
  it("replays the folded partition to the same validated state as the full history", () => {
    const f = buildFixture();
    const folded = applyFold(f.full, journalFoldPolicy());
    expect(folded.length).toBeLessThan(f.full.length);
    // The fold only removes: every survivor is the exact original frame.
    const bySeq = new Map(f.full.map((record) => [record.seq, record]));
    for (const record of folded) expect(bySeq.get(record.seq)).toBe(record);
    expect(folded.map((record) => record.seq)).toEqual(
      [...folded.map((record) => record.seq)].sort((a, b) => a - b),
    );

    const fullJournal = new ListJournal("global", f.full, f.nextSeq);
    const foldedJournal = new ListJournal("global", folded, f.nextSeq);
    const fullState = replay(fullJournal.asJournal());
    const foldedState = replay(foldedJournal.asJournal());
    expect(observe(foldedState, f)).toEqual(observe(fullState, f));
    // Recovery side effects (interrupted commands and questions, the quota
    // recovery marker) are identical, and both start after the disk nextSeq.
    // The marker digest covers the projection in Map-insertion order (see
    // `observe`), so it is the one order-dependent field.
    const appended = (journal: ListJournal) =>
      journal
        .appended()
        .map(([type, payload]) => [
          type,
          type === "quota.projection.updated"
            ? { ...(payload as object), projection_signature: "<order-dependent>" }
            : payload,
        ]);
    expect(appended(foldedJournal)).toEqual(appended(fullJournal));
    expect(fullJournal.appended().map(([type]) => type)).toEqual([
      "command.updated",
      "command.updated",
      "interaction.resolved",
      "quota.projection.updated",
    ]);
    expect(foldedJournal.records().at(-1)?.seq).toBe(fullJournal.records().at(-1)?.seq);
    // The crash-recovery path still finds run-e's durable terminal after the fold.
    expect(foldedState.commands.get("job-e")).toMatchObject({
      state: "interrupted",
      errorCode: "legacy_terminal_recovery_unavailable",
    });
    expect(foldedState.commands.get("job-c")).toMatchObject({ state: "interrupted" });
    // Disclosed delta: a settled question of a finished run reads "missing"
    // instead of "resolved" once its pair is forgotten (both are non-delivery).
    expect(fullState.interactions.status("run-a", "int-1")).toBe("resolved");
    expect(foldedState.interactions.status("run-a", "int-1")).toBe("missing");
  });

  it("never leaves a partial pair, a headless update or two terminals behind", () => {
    const f = buildFixture();
    const folded = applyFold(f.full, journalFoldPolicy());
    const types = (type: string) => folded.filter((record) => record.type === type);
    const accepted = new Set(
      types("command.accepted").map((r) => (r.payload as { record: { id: string } }).record.id),
    );
    for (const update of types("command.updated")) {
      expect(accepted.has((update.payload as { record: { id: string } }).record.id)).toBe(true);
    }
    expect([...accepted].sort()).toEqual(["job-a", "job-c", "job-e", "job-m"]);
    expect(types("command.pruned")).toEqual([]);
    const terminals = types("run.event")
      .map((r) => r.payload as { run_id: string; type: string })
      .filter((e) => ["run.completed", "run.failed", "run.blocked"].includes(e.type));
    expect(new Set(terminals.map((e) => e.run_id)).size).toBe(terminals.length);
    // A finished run keeps exactly its terminal; a live run keeps its progress.
    const eventsOf = (run: string) =>
      types("run.event")
        .map((r) => r.payload as { run_id: string; type: string })
        .filter((e) => e.run_id === run)
        .map((e) => e.type);
    expect(eventsOf("run-a")).toEqual(["run.completed"]);
    expect(eventsOf("run-e")).toEqual(["run.completed"]);
    expect(eventsOf("run-c")).toEqual(["run.created", "interaction.requested", "output.ready"]);
    // Interaction pairs: no resolution survives, and every surviving request is
    // one the full history still had pending.
    expect(types("interaction.resolved")).toEqual([]);
    expect(
      types("interaction.requested").map(
        (r) => (r.payload as { interactionId: string }).interactionId,
      ),
    ).toEqual(["int-3"]);
    // Quota pairs: a surviving commit upsert keeps its prepare adjacent.
    const fullBySeq = new Map(f.full.map((record) => [record.seq, record]));
    const retained = new Set(folded.map((record) => record.seq));
    for (const upsert of types("quota.snapshot.upserted")) {
      if (fullBySeq.get(upsert.seq - 1)?.type === "quota.snapshot.scoped_prepared") {
        expect(retained.has(upsert.seq - 1)).toBe(true);
      }
    }
    expect(types("quota.projection.updated")).toHaveLength(1);
    expect(types("thread.head.updated")).toHaveLength(1);
    expect(types("future.unknown")).toHaveLength(1);
    expect(types("journal.partition_quarantined")).toHaveLength(1);
  });
});
