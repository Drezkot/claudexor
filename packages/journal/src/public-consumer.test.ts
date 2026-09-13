import { mkdirSync, mkdtempSync, realpathSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
// Public self-reference resolves the built package's exported index.d.ts, not src.
import {
  DurableJournal,
  JournalRecoveryRequiredError,
  keepEverything,
  type FoldRecord,
  type FoldVerdict,
  type JournalCompactionDeclined,
  type JournalCompactionOutcome,
  type JournalCompactionReceipt,
  type JournalFold,
  type JournalRecoveryLocation,
} from "@claudexor/journal";

/** The daemon supplies the policy through exactly this shape. */
function verdictFor(record: FoldRecord): FoldVerdict {
  return record.type === "example"
    ? { slot: `example/${record.seq}` }
    : keepEverything.verdict(record);
}

describe("published journal API", () => {
  it("retains immediate receipt/null and void close beside the typed Promise API", async () => {
    const root = realpathSync.native(mkdtempSync(join(tmpdir(), "journal-consumer-")));
    const stagingDir = join(root, "stage");
    mkdirSync(stagingDir);
    const fold: JournalFold = { verdict: verdictFor };
    const journal = new DurableJournal({
      rootDir: join(root, "journal"),
      partition: "global",
      deferCompaction: true,
      compactionThresholdBytes: 0,
      fold,
    });
    try {
      journal.append("example", { text: "repeated ".repeat(1024) });
      const receipt: { beforeBytes: number; afterBytes: number; records: number } | null =
        journal.compact();
      expect(receipt?.records).toBe(1);
      expect(receipt).not.toHaveProperty("then");
      const location: JournalRecoveryLocation = {
        kind: "cursor",
        epoch: journal.currentEpoch(),
        seq: 1,
      };
      const recovery = new JournalRecoveryRequiredError({
        status: "recovery_required",
        location,
        reason: "public consumer diagnostic",
        discardedTailBytes: 0,
      });
      expect(recovery.recovery.location).toEqual(location);
      const future: Promise<JournalCompactionOutcome> = journal.compactInBackground({ stagingDir });
      const outcome = await future;
      if ("declined" in outcome) {
        const declined: JournalCompactionDeclined = outcome;
        expect(declined.reason).toBe("no_reclaim");
      } else {
        const installed: JournalCompactionReceipt = outcome;
        expect(installed.retainedCount).toBe(installed.records);
      }
      const closed: void = journal.close();
      expect(closed).toBeUndefined();
    } finally {
      journal.close();
      rmSync(root, { recursive: true, force: true });
    }
  });
});
