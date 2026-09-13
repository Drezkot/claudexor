import { createHash } from "node:crypto";
import { JournaledRunCreatedPayload, type RunEvent, type RunEventType } from "@claudexor/schema";

/**
 * Run events whose copy the owning global/project journal partition keeps
 * durably: the lifecycle-significant subset (run announced, a question asked
 * or resolved, output ready, terminal). Per-token `harness.event` deltas and
 * every other progress event reach only the per-run `events.jsonl` and the
 * in-process bus. Consumers of the journaled copy: the daemon's durable
 * terminal recovery (terminal types only) and the global journal stream, whose
 * macOS client reacts to `run.created`, `interaction.requested` and terminals.
 */
export const JOURNALED_RUN_EVENT_TYPES: ReadonlySet<RunEventType> = new Set<RunEventType>([
  "run.created",
  "interaction.requested",
  "interaction.answered",
  "interaction.timeout",
  "output.ready",
  "run.completed",
  "run.failed",
  "run.blocked",
]);

export function isJournaledRunEvent(event: Pick<RunEvent, "type">): boolean {
  return JOURNALED_RUN_EVENT_TYPES.has(event.type);
}

/**
 * The journal copy of `run.created` carries the prompt's sha256 and byte
 * length instead of the prompt text (the accepted command already holds the
 * prompt; the per-run `events.jsonl` keeps it too). Every other journaled event
 * is stored exactly as emitted.
 */
export function journaledRunEventCopy(event: RunEvent): RunEvent {
  if (event.type !== "run.created") return event;
  const { prompt, ...rest } = event.payload;
  if (typeof prompt !== "string") return event;
  return {
    ...event,
    payload: JournaledRunCreatedPayload.parse({
      ...rest,
      prompt_sha256: createHash("sha256").update(prompt, "utf8").digest("hex"),
      prompt_bytes: Buffer.byteLength(prompt, "utf8"),
    }),
  };
}
