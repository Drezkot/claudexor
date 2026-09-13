import { descriptorSize, readFrames, type FrameReadResult } from "./frame-reader.js";
import { readIntent, removeFile, truncatePendingSuffix } from "./journal-files.js";
import type { JournalFold } from "./journal-fold.js";
import { JournalRecoveryRequiredError, journalRecoveryAt } from "./journal-recovery-state.js";

export interface RecoveredJournal {
  retained: FrameReadResult["retained"];
  epoch: string | null;
  nextSeq: number;
  previousFrameHash: string;
  knownFileBytes: number;
  discardedBytes: number;
}

/** Recover only the original canonical file. A compaction candidate is never
 * consulted as recovery authority. Returns the retained ACK history for its
 * writer plus the chain state of the last frame on disk. */
export function recoverJournal(
  fd: number,
  path: string,
  options: { partition: string; fold?: JournalFold },
  intentPath: string,
): RecoveredJournal {
  const size = descriptorSize(fd);
  let decoded: FrameReadResult;
  let knownFileBytes = size;
  let discardedBytes = 0;
  try {
    const intent = readIntent(intentPath);
    if (intent) {
      if (intent.offset > size || size > intent.offset + intent.length) {
        throw required(intent.offset, "append intent does not match the journal prefix");
      }
      decoded = readFrames(fd, options.partition, { limit: intent.offset, fold: options.fold });
      if (decoded.error || decoded.incompleteOffset !== null) {
        throw required(intent.offset, "append intent does not match the journal prefix");
      }
      discardedBytes = size - intent.offset;
      if (discardedBytes > 0) truncatePendingSuffix(fd, path, intent.offset, size);
      knownFileBytes = intent.offset;
      removeFile(intentPath);
    } else {
      decoded = readFrames(fd, options.partition, { fold: options.fold });
    }
  } catch (error) {
    if (error instanceof JournalRecoveryRequiredError) throw error;
    throw required(0, `append intent is malformed: ${String(error)}`);
  }
  if (decoded.incompleteOffset !== null)
    throw required(decoded.incompleteOffset, "unexplained suffix without append intent");
  if (decoded.error) throw required(decoded.error.offset, decoded.error.reason);
  return {
    retained: decoded.retained,
    epoch: decoded.epoch,
    nextSeq: decoded.nextSeq,
    previousFrameHash: decoded.previousFrameHash,
    knownFileBytes,
    discardedBytes,
  };
}

function required(byteOffset: number, reason: string): JournalRecoveryRequiredError {
  return new JournalRecoveryRequiredError(journalRecoveryAt(byteOffset, reason));
}
