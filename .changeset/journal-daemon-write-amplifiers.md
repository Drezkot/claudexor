---
"@claudexor/daemon": minor
"@claudexor/cli": minor
"@claudexor/schema": minor
---

The daemon stops writing dead history into its journal and forgets it on replay. Per-token harness deltas no longer reach the journal (the per-run event log and the live stream keep them), the journaled `run.created` carries the prompt's digest instead of its text, `command.updated` frames omit the immutable params, quota snapshots are journaled only when their evidence changes and the projection marker carries a digest, and the retained params of terminal commands are capped by a code constant. Every partition replays and compacts through the daemon's fold policy, so startup memory follows the retained state rather than the file; crash-GC reads project roots from the already prepared command projection instead of replaying the journal a second time, journaled run events are validated once per generation, and journal maintenance re-requests itself when the file crosses the threshold again while logging typed declines and `journal.records_retired` receipts. An engine from before this change refuses a served root loudly.
