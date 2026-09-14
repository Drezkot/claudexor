import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  realpathSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { setImmediate } from "node:timers/promises";
import { DurableJournal } from "@claudexor/journal";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { JournalManager } from "./journal-manager.js";
import { JournalMaintenance } from "./journal-maintenance.js";

let root: string;
const managers: JournalManager[] = [];
const journals: DurableJournal[] = [];
const queues: JournalMaintenance[] = [];
beforeEach(() => {
  root = realpathSync.native(mkdtempSync(join(tmpdir(), "journal-maintenance-")));
});
afterEach(async () => {
  for (const queue of queues.splice(0)) await queue.stop();
  for (const manager of managers.splice(0)) manager.close();
  for (const journal of journals.splice(0)) journal.close();
  vi.restoreAllMocks();
  rmSync(root, { recursive: true, force: true });
});
function queue() {
  const warn = vi.fn();
  const note = vi.fn();
  const maintenance = new JournalMaintenance(root, warn, note);
  queues.push(maintenance);
  return { maintenance, warn, note };
}
function journal(partition: string, large = false) {
  const value = new DurableJournal({
    rootDir: join(root, "journal"),
    partition,
    deferCompaction: true,
  });
  journals.push(value);
  value.append("history", { text: large ? "x".repeat(9 * 1024 * 1024) : "small" });
  return value;
}
function manager(partition: string, requestMaintenance?: (journal: DurableJournal) => void) {
  const value = new JournalManager(root, { partition, requestMaintenance });
  managers.push(value);
  const slot = value.registerProjection({
    name: "probe",
    create: (journal: DurableJournal) => journal,
    validate: (journal: DurableJournal) => {
      journal.records(0, ["recovered"]);
    },
    recover: (journal: DurableJournal) => {
      if (!journal.records(0, ["recovered"]).length) journal.append("recovered", true);
    },
  });
  return { value, slot };
}

describe("journal maintenance generations", () => {
  it("wires the fresh quarantine generation while preserving its new epoch", () => {
    const original = journal("project:recover");
    const oldCursor = original.currentCursor();
    original.close();
    const bytes = readFileSync(original.path);
    bytes[0] = bytes[0]! ^ 0xff;
    writeFileSync(original.path, bytes, { mode: 0o600 });
    const request = vi.fn<(journal: DurableJournal) => void>();
    const value = new JournalManager(root, {
      partition: "project:recover",
      requestMaintenance: request,
    });
    managers.push(value);
    const slot = value.registerProjection({
      name: "probe",
      create: (journal: DurableJournal) => journal,
      validate: (journal: DurableJournal) => {
        journal.records();
      },
    });
    const inspection = value.start();
    expect(inspection.status).toBe("recovery_required");
    expect(request).not.toHaveBeenCalled();
    value.quarantineAndStartFresh({
      idempotencyKey: "recover",
      expectedFingerprint: inspection.fingerprint,
      confirmation: "quarantine_and_start_fresh",
    });
    expect(request).toHaveBeenCalledExactlyOnceWith(slot.current());
    expect(slot.current().options.deferCompaction).toBe(true);
    expect(() => slot.current().sequenceAfter(oldCursor)).toThrow(/stale/);
    expect(slot.current().records()[0]!.type).toBe("journal.partition_quarantined");
  });

  it("preserves inline defaults and defers opted-in activation until normal admission", async () => {
    const original = journal("global", true);
    const before = original.physicalBytes();
    original.close();
    const { maintenance } = queue();
    const request = vi.fn(maintenance.request);
    const deferred = manager("global", request);
    deferred.value.prepare();
    expect(request).not.toHaveBeenCalled();
    deferred.value.activatePrepared();
    expect(request).not.toHaveBeenCalled();
    expect(deferred.slot.current().physicalBytes()).toBe(before);
    deferred.value.recoverAfterStartup();
    const active = deferred.slot.current();
    const cursor = active.currentCursor();
    expect(request).toHaveBeenCalledWith(active);
    expect(active.records(0, ["recovered"])).toHaveLength(1);
    expect(active.options.deferCompaction).toBe(true);
    await setImmediate();
    expect(active.physicalBytes()).toBeGreaterThanOrEqual(before);
    maintenance.arm();
    await vi.waitFor(() => expect(active.physicalBytes()).toBeLessThan(before));
    expect(active.sequenceAfter(cursor)).toBe(2);
    const defaultSeed = journal("project:default", true);
    defaultSeed.close();
    const inline = manager("project:default");
    inline.value.start();
    expect(inline.slot.current().options.deferCompaction).toBe(false);
    // A daemon manager always folds, and a fold implies the seq-preserving
    // background path: the lossless synchronous compaction (new epoch, records
    // renumbered by index) is skipped at open, so without a maintenance
    // callback the file only grows by the recovery append.
    expect(inline.slot.current().physicalBytes()).toBeGreaterThanOrEqual(before);
    expect(inline.slot.current().atCompactionThreshold()).toBe(true);
  });

  it("runs one flight at a time, serializes partitions, and aborts/drains at stop", async () => {
    const first = journal("global");
    const second = journal("project:other");
    let active = 0;
    let maximum = 0;
    const calls: DurableJournal[] = [];
    const ended: DurableJournal[] = [];
    vi.spyOn(DurableJournal.prototype, "compactInBackground").mockImplementation(function (
      this: DurableJournal,
      options,
    ) {
      calls.push(this);
      active += 1;
      maximum = Math.max(maximum, active);
      return new Promise((resolve) => {
        options.signal!.addEventListener(
          "abort",
          () => {
            active -= 1;
            ended.push(this);
            resolve({ declined: true, reason: "aborted" });
          },
          { once: true },
        );
      });
    });
    const { maintenance } = queue();
    maintenance.request(first);
    maintenance.request(first);
    maintenance.request(second);
    await setImmediate();
    expect(calls).toEqual([]);
    maintenance.arm();
    await vi.waitFor(() => expect(calls).toEqual([first]));
    maintenance.request(first);
    const stopped = maintenance.stop();
    expect(ended).toEqual([first]); // synchronous abort prefix
    await stopped;
    maintenance.request(second);
    maintenance.arm();
    await setImmediate();
    expect(calls).toEqual([first]);
    expect(maximum).toBe(1);
  });

  it("re-requests a generation after its flight settles and logs typed outcomes", async () => {
    const first = journal("global");
    const second = journal("project:second");
    const calls = vi
      .spyOn(DurableJournal.prototype, "compactInBackground")
      .mockRejectedValueOnce(new Error("preparation failed"))
      .mockResolvedValueOnce({ declined: true, reason: "no_reclaim", compressedBytes: 10, cap: 5 })
      .mockResolvedValueOnce({ declined: true, reason: "below_threshold" })
      .mockResolvedValue({
        beforeBytes: 100,
        afterBytes: 40,
        records: 3,
        retainedCount: 3,
        retiredCount: 7,
        retiredBytes: 60,
      });
    const { maintenance, warn, note } = queue();
    maintenance.request(first);
    maintenance.request(second);
    maintenance.arm();
    await vi.waitFor(() => expect(calls).toHaveBeenCalledTimes(2));
    expect(warn).toHaveBeenCalledWith(expect.stringContaining("preparation failed"));
    expect(note).toHaveBeenCalledWith(
      "journal.compaction_declined partition=project:second reason=no_reclaim compressedBytes=10 cap=5",
    );
    // A failed or declined generation is not condemned: the threshold hook
    // re-requests it after the next crossing, and the queue runs it again.
    maintenance.request(first);
    maintenance.request(second);
    await vi.waitFor(() => expect(calls).toHaveBeenCalledTimes(4));
    expect(note).toHaveBeenCalledTimes(2); // below_threshold stays silent
    expect(note).toHaveBeenLastCalledWith(
      "journal.records_retired partition=project:second retainedCount=3 retiredCount=7 retiredBytes=60 retiredAtReplayCount=0 retiredAtReplayBytes=0 beforeBytes=100 afterBytes=40",
    );
    const third = journal("project:new");
    maintenance.request(third);
    await vi.waitFor(() => expect(calls).toHaveBeenCalledTimes(5));
  });

  it("hears every threshold crossing: a second crossing after an install runs another pass", async () => {
    const { maintenance, note } = queue();
    const { value, slot } = manager("global", maintenance.request);
    value.start(); // recoverAfterStartup requests once: below threshold, silent
    maintenance.arm();
    const journal = slot.current();
    const big = () => ({ text: "x".repeat(9 * 1024 * 1024) });
    journal.append("history", big()); // crosses: the journal's hook requests a pass
    await vi.waitFor(
      () => expect(note).toHaveBeenCalledWith(expect.stringContaining("journal.records_retired")),
      { timeout: 20_000 },
    );
    expect(note).toHaveBeenLastCalledWith(
      expect.stringMatching(
        /^journal\.records_retired partition=global retainedCount=\d+ retiredCount=0 retiredBytes=0 retiredAtReplayCount=0 retiredAtReplayBytes=0 beforeBytes=\d+ afterBytes=\d+$/,
      ),
    );
    const compacted = journal.physicalBytes();
    expect(compacted).toBeLessThan(9 * 1024 * 1024);
    // The install re-armed the hook: the next crossing is heard through the
    // in-flight dedupe and runs one more pass, not swallowed.
    journal.append("history", big());
    await vi.waitFor(() => expect(note).toHaveBeenCalledTimes(2), { timeout: 20_000 });
    expect(journal.physicalBytes()).toBeLessThan(compacted + 9 * 1024 * 1024);
    expect(journal.atCompactionThreshold()).toBe(false);
  });

  it("coalesces requests that arrive while the same generation is in flight into one more pass", async () => {
    const first = journal("global");
    let release: (() => void) | null = null;
    const calls = vi.spyOn(DurableJournal.prototype, "compactInBackground").mockImplementation(
      () =>
        new Promise((resolve) => {
          release = () => resolve({ declined: true, reason: "below_threshold" });
        }),
    );
    const { maintenance } = queue();
    maintenance.request(first);
    maintenance.arm();
    await vi.waitFor(() => expect(calls).toHaveBeenCalledTimes(1));
    maintenance.request(first);
    maintenance.request(first);
    maintenance.request(first);
    await setImmediate();
    expect(calls).toHaveBeenCalledTimes(1);
    release!();
    await vi.waitFor(() => expect(calls).toHaveBeenCalledTimes(2));
    release!();
    await setImmediate();
    await setImmediate();
    expect(calls).toHaveBeenCalledTimes(2);
  });

  it("retires an archived generation before rename and never publishes its pending candidate", async () => {
    const seed = journal("project:archive", true);
    seed.close();
    const { maintenance } = queue();
    const owned = manager("project:archive", maintenance.request);
    owned.value.start();
    const old = owned.slot.current();
    const before = readFileSync(old.path);
    const archive = owned.value.archivePartition()!;
    maintenance.arm();
    await setImmediate();
    await maintenance.stop();
    expect(() => old.state()).toThrow(/closed/);
    // Compare the complete bytes without expanding a multi-MiB Buffer into matcher entries.
    expect(readFileSync(join(archive, "journal.bin")).equals(before)).toBe(true);
  });

  it("cleans only owned crash candidates after arm, preserving all other files", async () => {
    const staging = join(root, "journal-compaction");
    mkdirSync(staging);
    const stale = "journal-compaction-12345678-abcd-1234-abcd-123456789abc.compact";
    writeFileSync(join(staging, stale), "scratch", { mode: 0o600 });
    writeFileSync(join(staging, "append.pending.json"), "unrelated", { mode: 0o600 });
    const { maintenance } = queue();
    maintenance.request(journal("global"));
    await setImmediate();
    expect(readdirSync(staging)).toContain(stale);
    maintenance.arm();
    await vi.waitFor(() => expect(readdirSync(staging)).toEqual(["append.pending.json"]));
  });
});
