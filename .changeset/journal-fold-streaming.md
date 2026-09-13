---
"@claudexor/journal": minor
---

The durable journal now replays its file frame by frame instead of loading it whole, so daemon startup memory follows the retained record set rather than the journal size. Callers may supply a fold policy that is applied at replay and at background compaction; sequence numbers, the epoch and live cursors are preserved across compaction, dead records are dropped from the file per that policy, snapshots may span several frames, background maintenance re-requests itself when the file crosses the threshold again, and a declined maintenance pass is reported with a typed reason instead of `null`. An engine from before this change refuses a folded journal loudly rather than reading a partial history.
