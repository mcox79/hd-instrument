# Orchestrator -> Research: results summary cycle 190 (v516 / commit d73331c4)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-08 ~12:30
**Trigger:** verdict_handler dispatch w/ cap_map state change. 2-batch scale-ups.

## Headline

- 2 HP, 0 LVH. PP-145 + PP-135 annotated (no new rows; existing rows extended). Portfolio 32+152 unchanged.
- `wikipedia_ingest_100k` HP: r@5=0.992 at 100k articles, 152 art/sec. 10× scale-up from cycle-187 10k HP. PP-145 scale ladder extended; next gate is 500k or 1M.
- `n1_pythia2p8b_substrate_kv` HP: M=2000, recall=1.000 at Pythia-2.8B. PP-135 LLM-keyed external KV confirmed size-agnostic across base / 1.4B / 2.8B with identical metrics.

## Findings

- `wikipedia_ingest_100k_gpu` HP: r@5=0.992, 152 articles/sec at 100k. 10× past cycle-187 10k HP at no meaningful recall drop. PP-145 annotated.
- `n1_pythia2p8b_substrate_kv_gpu` HP: M=2000, recall=1.000 at Pythia-2.8B. Three model sizes (base / 1.4B / 2.8B) at identical perfect recall with in-context window holding only 3%. PP-135 annotated.

## State

- cap_map v515 → v516
- commit: d73331c4
- HONEST 1406 → 1408 (+2)
- LVH 263 unchanged
- Portfolio 32+152 unchanged (PP-145 + PP-135 annotated)

## Context

Both anchors are scale-ups of existing HP capabilities, not new rows. PP-145 (Wikipedia ingest, cycle 187) extends from 10k → 100k with r@5 essentially flat (0.992 vs 0.992 at 10k). The 5.84M gate now has two clean checkpoints on the scale ladder; 500k or 1M is the next checkpoint. Band-LIFT to VALIDATED is a candidate after 3-seed promotion at 100k.

PP-135 (LLM-keyed external KV, cycle 185) extends from Pythia-1.4B → Pythia-2.8B with identical recall=1.000 at M=2000. Three model sizes (Pythia-base, Pythia-1.4B, Pythia-2.8B) now all show ceiling recall with only 3% of facts fitting the in-context window. The capability is size-agnostic across the tested range. Next gates are 3-seed promotion, M-sweep to probe the capacity ceiling, and a non-Pythia encoder test.

CPU continues to run `legal_citation_1000seed` (since 11:25, ~65 min wall now — extending PP-120 from 500 to 1000 seeds). CPU queue depth 13 pending.

Pipeline: 75 commits v438→v516. 455 anchors verdicted. 39 LVH catches.

---

END. No action requested.
