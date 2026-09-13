import { mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it, vi } from "vitest";
import { DurableJournal } from "./index.js";

// Scale only the existing logical cap; count real UTF-8 bytes at its exact edge.
vi.mock("./frame-codec.js", async (original) => ({
  ...(await original<typeof import("./frame-codec.js")>()),
  MAX_COMPACTED_LOGICAL_BYTES: 512,
}));
describe("background logical capacity", () => {
  it.each([512, 513])("handles %s logical UTF-8 bytes without trimming", async (bytes) => {
    const root = realpathSync.native(mkdtempSync(join(tmpdir(), "journal-capacity-")));
    const stagingDir = join(root, "staging");
    mkdirSync(stagingDir);
    const now = () => new Date("2026-01-01T00:00:00Z");
    const journal = new DurableJournal({
      rootDir: join(root, "journal"),
      partition: "global",
      deferCompaction: true,
      compactionThresholdBytes: 0,
      now,
    });
    try {
      // A seq-preserving snapshot stores `{seq,time,type,payload}` per record.
      const prefixBytes = Buffer.byteLength(
        JSON.stringify([
          { seq: 1, time: now().toISOString(), type: "record", payload: { text: "é" } },
        ]),
      );
      journal.append("record", { text: "é" + "x".repeat(bytes - prefixBytes) });
      const before = readFileSync(journal.path);
      const logical = journal.records().map(({ time, type, payload }) => ({ time, type, payload }));
      const stored = journal
        .records()
        .map(({ seq, time, type, payload }) => ({ seq, time, type, payload }));
      expect(Buffer.byteLength(JSON.stringify(stored))).toBe(bytes);
      const result = await journal.compactInBackground({ stagingDir });
      if (bytes === 512) expect(result).toMatchObject({ records: 1, retainedCount: 1 });
      else {
        // A single record that can never decode within the guard is refused typed.
        expect(result).toEqual({ declined: true, reason: "capacity", cap: 16 * 1024 * 1024 });
        expect(readFileSync(journal.path)).toEqual(before);
      }
      expect(journal.state().status).toBe("ready");
      expect(journal.records().map(({ time, type, payload }) => ({ time, type, payload }))).toEqual(
        logical,
      );
      expect(journal.append("after.capacity", true).seq).toBe(2);
    } finally {
      journal.close();
      rmSync(root, { recursive: true, force: true });
    }
  });
});
