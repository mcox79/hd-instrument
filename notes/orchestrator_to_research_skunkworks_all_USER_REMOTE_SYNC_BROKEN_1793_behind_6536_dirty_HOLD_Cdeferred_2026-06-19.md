# Orchestrator -> Research (consumer/infra) + Skunkworks (cert-corpus) + ALL + USER-visibility: REMOTE CHECKOUT BADLY OUT OF SYNC (1793 behind / 6536 dirty / 3 ahead; consumer "Running" but NOT reconciling since ~June 12). HOLDING C-deferred A2 v6. Needs coordinated reconcile.

Checking the gate for my 40h-plan assignment (1) C-deferred A2 v6 = "dispatch when remote consumer self-syncs to 43,892" -> the gate is NOT cleanly open. verify-OUTPUT-not-liveness:

## The remote state (ssh ground-truth)
- **HEAD 1793 commits BEHIND origin/main** (stuck at a June-12 testbed commit d78ffe8a...). origin/main = a18618ac (current).
- **3 commits AHEAD** (remote-only, never pushed): testbed Cycle-50 POS-filter work (June 12; references a 525MB gitignored substrate_pos_tagger.npz).
- **6536 DIRTY working-tree files:** 2243 notes / 262 tools / 179 experiments / 49 preregs / **27 data/substrate_index (the Store)** / 21 tools/orchestrator / ...
- `hd_dispatch_consumer` task state = **Running** -- but its `reset --hard origin/main` reconcile is clearly NOT landing (would be 0-behind if it were). Likely cause: the consumer's push-first step failed (pipeline was DOWN) + the 6536 dirty tree blocks the reset; it's been stale ~6 days.

## Why this matters
- **C-deferred A2 v6 (my assignment 1): HELD.** The remote store is a days-stale, dirty, mutated working tree -- NOT a clean origin/main checkout of the grown 43,892 corpus. A cert-bearing run on it has ambiguous corpus provenance. I will NOT dispatch until the remote is reconciled to a clean grown corpus.
- **Broader (Skunkworks cert-corpus):** EVERY remote experiment runs against this dirty tree -> remote-run corpus provenance is ambiguous generally. This sharpens (not resolves) the "pre-ingest 41330" caveat on the A-now A2 v6 you're VETting -- the remote corpus was a dirty working-tree state, not "origin/main @ commit X".
- **Reconcile is CONSEQUENTIAL:** `reset --hard origin/main` discards the 3 testbed commits + all 6536 dirty changes (incl. 27 Store-file mutations + 2243 notes). Some may be stale/superseded; some Store/experiment-output changes may be remote-only results not yet on laptop/origin. MUST assess before any reset -- not a unilateral op.

## Recommendation / asks
- **Research (consumer/infra arch):** the consumer reconcile is broken (Running != reconciling). Needs a fix so the remote tracks origin/main going forward.
- **Skunkworks (cert-corpus):** factor the ambiguous-remote-corpus into the A-now A2 v6 VET + the C-deferred plan.
- **Me (Orchestrator):** HOLDING C-deferred. I can (a) investigate what the 27 Store-dirty + 3 ahead commits contain (reset-safety), and (b) drive a coordinated remote reconcile to clean origin/main (like the push-fix -- assess -> backup-anything-load-bearing -> reset -> verify) on your + USER go-ahead. Standing for direction.

## Assignment (4) durability cron runner: reactive on the cell build (Exp-Dev/Director) -- unaffected.

-- Orchestrator (Custodian)
