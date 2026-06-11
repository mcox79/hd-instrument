# exp_dev hand-off -- research: free-probability F4 + family-tag inventory expansion 2x

Filed-by: research sub-agent (2026-06-11)
Trigger: Combined 2x DEEP drill on Tier-1 advisor candidate F4 free cumulants + Tier-2 family-tag inventory expansion
Research note: d:/AI/hd-instrument/notes/research_drill_free_probability_family_tag_2x_2026-06-11.md

## Pause state block

This file is auto-discoverable on exp_dev emergency-refill cycles.
Experiments proposed here are NEW anchors, not re-runs of existing ones.
All cells are CPU-feasible. No cloud needed. No GPU needed.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev has full autonomy
over anchor names, sweep parameters, numerical thresholds, queue choice,
and pre-reg bands. This file provides TASK + WHY + CONTRACT only.

---

## Anchor Candidates (rank-ordered)

### Rank 1 -- F4 baseline-vs-substrate diagnostic (CELL-F4-DIAG)
Why now: Single-formula observability check. ~50 lines numpy. Under 5 minutes
laptop CPU. First-ever test of whether substrate concept-embedding overlap
distribution differs from iid-uniform-on-sphere at second-order-free moment.
Substrate-product reading: if F4(substrate) is empirically indistinguishable
from F4(iid-sphere) within bootstrap CI, the substrate's storage layer has no
surplus relational structure over flat random vectors -- a major finding either
way. If clearly different, F4 becomes a permanent dashboard metric.
Tier hint: CPU smoke; bootstrap n=1000 on N=10K embedding pairs.
Anchor pointer: free_kappa4 (free cumulant order 4) baseline vs substrate.
Reference path: notes/research_drill_free_probability_family_tag_2x_2026-06-11.md Section 1.

### Rank 2 -- F4 self-index ablation (CELL-F4-SELFINDEX)
Why now: F4 is the cheapest observability test for "does substrate-self-index
do anything to relational geometry beyond what flat cosine sees". Gates the
self-index design narrative without round-trip task accuracy.
Substrate-product reading: any clear F4 movement from self-index = self-index is
doing something measurable, direction tells you what (whitening vs concentrating
structure). Null movement = self-index is a no-op at second-order-free level.
Tier hint: CPU; compare F4 across {raw embeddings, self-index variant A, variant B, ...}.
Anchor pointer: free_kappa4 sweep across substrate-self-index variants.
Reference path: same research note Section 1.5.

### Rank 3 -- Family-tag inventory enumeration audit (CELL-TAGS-AUDIT)
Why now: Pure CPU enumeration. No model runs. Validates that the 27-tag inventory
covers >= 95% of sub-ops named in cap_map + feedback memory index without
double-assignment ambiguity. If it fails, the inventory needs adjustment BEFORE
becoming load-bearing infrastructure.
Substrate-product reading: produces the substrate's first principled ontology,
usable as documentation index + per-shard protection partition + Tier-2 cluster
definition. Failed audit forces re-derivation of the role axes.
Tier hint: CPU; pure enumeration; ~1 hour.
Anchor pointer: family_tag_inventory_27 vs cap_map+feedback sub-op corpus.
Reference path: same research note Section 2.

### Rank 4 -- Within-family vs cross-family F4 (CELL-F4-FAMILY)
Why now: Once Rank 1 and Rank 3 are done, the natural composition is to compute
F4 conditioned on family-tag membership. Reveals whether different families have
qualitatively different relational geometries. This is a substrate-novel feature
that flat-cosine baselines literally cannot provide.
Substrate-product reading: enables family-aware retrieval grounded in measurable
observable; produces empirically-justified per-family retrieval tuning.
Tier hint: CPU; depends on Rank 1 + Rank 3 completion.
Anchor pointer: free_kappa4 within-family vs cross-family conditional decomposition.
Reference path: same research note Section "Product Implication 3".

---

## Context pointers (file paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_free_probability_family_tag_2x_2026-06-11.md  -- full drill note
- d:/AI/hd-instrument/notes/substrate_capability_map.md  -- cap_map sub-op inventory for Rank 3 audit input
- d:/AI/hd-instrument/notes/research_meta_map_and_adjacencies_2026-05-21.md  -- field-adjacency context for free-probability anchor
- C:/Users/marsh/.claude/projects/d--AI/memory/MEMORY.md  -- feedback memory index for Rank 3 audit input
- d:/AI/hd-instrument/data/orchestrator_status_log.jsonl  -- prior research_delivery entries to avoid re-drilling

## Contract

- Pre-reg per envelope-fail-bands BEFORE running.
- HARD-PASS / HARD-FAIL thresholds are SPECIFIED in the research note Section "Falsifiable predictions" -- copy them verbatim into the queue_add pre-reg.
- All cells: smoke-gate first; on smoke PASS, ship via queue_add; post-ship REMOTE VERIFY.
- Bootstrap CI is mandatory for any F4 reading.
- ASCII-only in cells, plain language, no emojis (per substrate code conventions in CLAUDE.md).
- Self-test per formula-selftests -- the F4 formula kappa_4 = m_4 - (1 + lambda) * m_2^2 has a single closed-form check: for centered semicircle of radius 2*sigma, kappa_4 = 0 exactly. This is the unit test.
- No GPU. No cloud. Local CPU queue (data/local_cpu_queue) sufficient for all 4 ranks.

## Autonomy declaration

exp_dev decides:
- Anchor names (suggestions: F4-DIAG / F4-SELFINDEX / TAGS-AUDIT / F4-FAMILY).
- Queue lane (local_cpu_queue recommended; GPU not needed).
- Sweep parameters (suggested bootstrap n=1000; embedding sample N=10K; comparison count >= 2 variants for Rank 2).
- Implementation order (Rank 1 + Rank 3 are independent and can run in parallel; Rank 2 depends on Rank 1; Rank 4 depends on Rank 1 and Rank 3).
- Whether to also surface Rank-5+ extensions (e.g. kappa_5 / kappa_6 once Rank 1 PASSES, or Tracy-Widom edge-fluctuation tests as a follow-up).

Research will accept any anchor naming and parameter choices that respect the contract above.
