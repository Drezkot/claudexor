import { randomUUID } from "node:crypto";
import { fstatSync, lstatSync, rmSync } from "node:fs";
import { join } from "node:path";
import { ensureCanonicalPrivateDirectory } from "@claudexor/util";
import { cloneJson, prepareAppendBatch } from "./append-batch.js";
import { ZERO_HASH, type JournalRecord } from "./frame-codec.js";
import {
  declinedCompaction,
  prepareJournalCompaction,
  type JournalCompactionOutcome,
} from "./journal-compaction.js";
import {
  prepareBackgroundCompaction,
  sameBoundary,
  type CompactionBoundary,
} from "./journal-background-compaction.js";
import { JournalCore, type DurableJournalOptions } from "./journal-core.js";
import {
  ensurePrivateFile,
  sameJournalFile,
  readIntent,
  removeFile,
  writeIntent,
} from "./journal-files.js";
import { sequenceAfterCursor, encodeCursor, JournalCursorError } from "./journal-cursor.js";
import { journalPartitionDirectory } from "./journal-partition.js";
import {
  fingerprintPreparedJournal,
  inspectPreparedJournal,
  type JournalPreparationReceipt,
  type PreparedJournalInspection,
} from "./read-only-preparation.js";
export type { JournalRecord, JournalPreparationReceipt, DurableJournalOptions };
export { JournalCursorError } from "./journal-cursor.js";
export { journalPartitionDirectory } from "./journal-partition.js";
export { JournalRecoveryRequiredError, JournalAppendUncertainError };
export type { JournalRecoveryLocation, JournalRecoveryState } from "./journal-recovery-state.js";
export type { FoldRecord, FoldVerdict, JournalFold } from "./journal-fold.js";
export { keepEverything } from "./journal-fold.js";
export type {
  JournalCompactionDeclined,
  JournalCompactionOutcome,
  JournalCompactionReceipt,
} from "./journal-compaction.js";
import {
  JournalRecoveryRequiredError,
  JournalAppendUncertainError,
  type JournalRecoveryState,
} from "./journal-recovery-state.js";

const PREPARED_JOURNAL = Symbol("prepared-journal");

/** Single-writer, checksummed journal. A returned append has reached fsync. */
export class DurableJournal extends JournalCore {
  static prepare(options: DurableJournalOptions): DurableJournal {
    if (!options.partition.trim()) throw new Error("journal partition must not be empty");
    const partitionDir = journalPartitionDirectory(options.rootDir, options.partition);
    const prepared = inspectPreparedJournal({
      rootDir: options.rootDir,
      partitionDir,
      journalPath: join(partitionDir, "journal.bin"),
      intentPath: join(partitionDir, "append.pending.json"),
      partition: options.partition,
      initialEpoch: (options.epochFactory ?? randomUUID)(),
      fold: options.fold,
    });
    const InternalJournal = DurableJournal as unknown as {
      new (
        value: DurableJournalOptions,
        token: typeof PREPARED_JOURNAL,
        inspection: PreparedJournalInspection,
      ): DurableJournal;
    };
    return new InternalJournal(options, PREPARED_JOURNAL, prepared);
  }

  constructor(options: DurableJournalOptions);
  constructor(
    options: DurableJournalOptions,
    token?: typeof PREPARED_JOURNAL,
    prepared?: PreparedJournalInspection,
  ) {
    super(options);
    if (token === PREPARED_JOURNAL && prepared) {
      this.preparationState = prepared.receipt;
      this.recovery = structuredClone(prepared.recovery);
      for (const record of prepared.records) this.entries.push(record);
      this.epoch = prepared.epoch;
      this.nextSeq = prepared.nextSeq;
      this.previousFrameHash = prepared.previousFrameHash;
      this.knownFileBytes = prepared.knownFileBytes;
      return;
    }
    ensureCanonicalPrivateDirectory(options.rootDir);
    this.epoch = (options.epochFactory ?? randomUUID)();
    ensureCanonicalPrivateDirectory(this.partitionDir);
    ensurePrivateFile(this.path);
    this.openWriter();
    this.recover();
    this.compactAtThreshold();
  }

  state(): JournalRecoveryState {
    this.assertOpen();
    return structuredClone(this.recovery);
  }

  preparation(): JournalPreparationReceipt {
    this.assertOpen();
    if (!this.preparationState) throw new Error("journal was not opened through preparation");
    return structuredClone(this.preparationState);
  }

  revalidatePreparation(): void {
    this.assertOpen();
    if (!this.preparationState) throw new Error("journal was not opened through preparation");
    const actual = fingerprintPreparedJournal(this.options.rootDir, this.partitionDir);
    if (
      actual.fingerprint !== this.preparationState.fingerprint ||
      actual.preparationIdentity !== this.preparationState.preparationIdentity
    ) {
      throw new Error("journal changed since read-only preparation");
    }
  }

  activatePrepared(): void {
    this.assertOpen();
    if (!this.preparationState) throw new Error("journal was not opened through preparation");
    if (this.recovery.status === "recovery_required") {
      this.closeWriter();
      throw new JournalRecoveryRequiredError(this.recovery);
    }
    if (this.writable) return;
    try {
      this.revalidatePreparation();
      ensureCanonicalPrivateDirectory(this.options.rootDir);
      ensureCanonicalPrivateDirectory(this.partitionDir);
      ensurePrivateFile(this.path);
      this.entries.length = 0;
      this.nextSeq = 1;
      this.previousFrameHash = ZERO_HASH;
      this.knownFileBytes = 0;
      this.recovery = { status: "ready", discardedTailBytes: 0 };
      this.openWriter();
      this.recover();
      const activatedRecovery = this.state();
      if (activatedRecovery.status === "recovery_required") {
        throw new JournalRecoveryRequiredError(activatedRecovery);
      }
      this.compactAtThreshold();
    } catch (error) {
      this.failPreparedActivation(error);
    }
  }

  /** Select exact types before copying payloads; sequence numbers and cursors
   * still belong to the complete journal. Omit types to read every record. */
  records<T = unknown>(afterSeq = 0, types?: readonly string[]): JournalRecord<T>[] {
    this.assertReadable();
    return this.entries
      .filter((record) => record.seq > afterSeq && (!types || types.includes(record.type)))
      .map((record) => ({ ...record, payload: cloneJson(record.payload) as T }));
  }

  close(): void {
    if (this.closed) return;
    this.background?.controller.abort();
    this.closed = true;
    this.closeWriter();
  }

  currentCursor(): string {
    this.assertReadable();
    return encodeCursor(this.options.partition, this.epoch, this.nextSeq - 1);
  }

  cursorAt(seq: number): string {
    this.assertReadable();
    if (!Number.isSafeInteger(seq) || seq < 0 || seq >= this.nextSeq) {
      throw new JournalCursorError("journal cursor sequence is outside the current epoch");
    }
    return encodeCursor(this.options.partition, this.epoch, seq);
  }

  currentSequence(): number {
    this.assertReadable();
    return this.nextSeq - 1;
  }

  currentEpoch(): string {
    this.assertReadable();
    return this.epoch;
  }

  physicalBytes(): number {
    this.assertOpen();
    return this.knownFileBytes;
  }

  /** Atomically replace physical frames with one checksummed compressed frame. */
  compact(): { beforeBytes: number; afterBytes: number; records: number } | null {
    this.background?.controller.abort();
    this.assertReadable();
    this.assertWritable();
    const result = prepareJournalCompaction({
      path: this.path,
      partition: this.options.partition,
      entries: this.entries,
      knownFileBytes: this.knownFileBytes,
      now: this.now,
    });
    if (!result) return null;
    try {
      this.installCompaction(result);
      return result.receipt;
    } finally {
      rmSync(result.path, { force: true });
    }
  }

  /** Automatic maintenance preserves logical epoch/seq cursors, including ACKed
   * appends during preparation, and applies the configured fold. The first
   * caller's signal owns a shared flight; a decline is typed, never silent. */
  compactInBackground(options: {
    stagingDir: string;
    signal?: AbortSignal;
  }): Promise<JournalCompactionOutcome> {
    if (this.background) return this.background.promise;
    this.assertReadable();
    this.assertWritable();
    if (options.signal?.aborted) return Promise.resolve(declinedCompaction("aborted"));
    if (!this.atCompactionThreshold())
      return Promise.resolve(declinedCompaction("below_threshold"));
    if (this.nextSeq <= 1) return Promise.resolve(declinedCompaction("empty"));
    const controller = new AbortController();
    const abort = () => controller.abort();
    options.signal?.addEventListener("abort", abort, { once: true });
    const entries = this.entries;
    const fd = this.fd;
    const epoch = this.epoch;
    const identity = fstatSync(fd);
    const current = (): CompactionBoundary => {
      controller.signal.throwIfAborted();
      this.assertReadable();
      this.assertWritable();
      if (this.entries !== entries || this.fd !== fd || this.epoch !== epoch)
        throw new Error("journal compaction generation changed");
      return {
        count: entries.length,
        nextSeq: this.nextSeq,
        previousFrameHash: this.previousFrameHash,
        knownFileBytes: this.knownFileBytes,
      };
    };
    const promise = prepareBackgroundCompaction({
      stagingDir: options.stagingDir,
      signal: controller.signal,
      partition: this.options.partition,
      epoch,
      time: this.now().toISOString(),
      entries,
      prefix: current(),
      fold: this.options.fold,
      current,
      install: (candidate, boundary) => {
        if (!sameBoundary(current(), boundary)) return false;
        const actual = fstatSync(fd);
        const path = lstatSync(this.path);
        if (
          !sameJournalFile(identity, actual, boundary.knownFileBytes) ||
          !sameJournalFile(identity, path, boundary.knownFileBytes) ||
          readIntent(this.intentPath())
        )
          throw new JournalRecoveryRequiredError(
            this.requireRecovery(
              boundary.knownFileBytes,
              "journal changed outside its single writer during compaction",
            ),
          );
        this.installCompaction(candidate);
        return true;
      },
    }).finally(() => {
      options.signal?.removeEventListener("abort", abort);
      if (this.background?.promise === promise) this.background = null;
    });
    this.background = { controller, promise };
    return promise;
  }

  sequenceAfter(cursor: string | null | undefined): number {
    this.assertReadable();
    return sequenceAfterCursor(cursor, this.options.partition, this.epoch, this.nextSeq);
  }

  cursorFor(record: Pick<JournalRecord, "partition" | "epoch" | "seq">): string {
    this.assertReadable();
    if (record.partition !== this.options.partition || record.epoch !== this.epoch) {
      throw new JournalCursorError("cannot encode a cursor for another partition or epoch");
    }
    return encodeCursor(record.partition, record.epoch, record.seq);
  }

  append<T>(type: string, payload: T): JournalRecord<T> {
    return this.appendBatch([{ type, payload }])[0] as JournalRecord<T>;
  }

  /** Append one logical record group with one intent and one fsync. Recovery
   * either retains the whole acknowledged group or truncates every group byte;
   * no prefix can become durable on its own. */
  appendBatch(records: readonly { type: string; payload: unknown }[]): JournalRecord[] {
    this.assertReadable();
    this.assertWritable();
    if (records.length === 0) throw new Error("journal append batch must not be empty");
    for (const record of records) {
      if (!record.type.trim()) throw new Error("journal record type must not be empty");
    }
    const actualBytes = Number(fstatSync(this.fd, { bigint: true }).size);
    if (actualBytes !== this.knownFileBytes) {
      throw new JournalRecoveryRequiredError(
        this.requireRecovery(this.knownFileBytes, "journal changed outside its single writer"),
      );
    }
    const batch = prepareAppendBatch({
      partition: this.options.partition,
      epoch: this.epoch,
      nextSeq: this.nextSeq,
      previousFrameHash: this.previousFrameHash,
      byteOffset: this.knownFileBytes,
      now: this.now,
      records,
    });
    const byteOffset = this.knownFileBytes;
    writeIntent(this.intentPath(), { v: 1, offset: byteOffset, length: batch.bytes.length });
    try {
      this.appendFrame(this.fd, batch.bytes);
      if (Number(fstatSync(this.fd, { bigint: true }).size) !== byteOffset + batch.bytes.length) {
        throw new Error("journal append did not write the complete batch");
      }
      removeFile(this.intentPath());
    } catch (error) {
      const recovery = this.requireRecovery(
        byteOffset,
        "append/fsync completion is uncertain; restart and inspect before further mutations",
      );
      throw new JournalAppendUncertainError(recovery, { cause: error });
    }
    for (const record of batch.records) this.entries.push(record);
    this.nextSeq = batch.nextSeq;
    this.previousFrameHash = batch.previousFrameHash;
    this.knownFileBytes += batch.bytes.length;
    this.notifyThreshold();
    return batch.records.map((record) => ({ ...record, payload: cloneJson(record.payload) }));
  }

  protected appendRecovered(type: string, payload: unknown): void {
    this.append(type, payload);
  }

  /** Edge-triggered: one notification per crossing, decoupled from the ACK
   * already returned to the appender; a successful install re-arms it. */
  private notifyThreshold(): void {
    const hook = this.options.onCompactionThreshold;
    if (!hook || this.thresholdNotified || !this.atCompactionThreshold()) return;
    this.thresholdNotified = true;
    queueMicrotask(hook);
  }

  private compactAtThreshold(): void {
    if (
      !this.options.deferCompaction &&
      this.recovery.status === "ready" &&
      this.atCompactionThreshold()
    )
      this.compact();
  }
}
