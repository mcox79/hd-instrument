# exp_dev hand-off — research: 5x DEEPER cross-corpus composition gap

**Filed-by.** research (Opus 4.7) 2026-06-23
**Trigger.** 5x DEEPER mechanism drill on `cross_corpus_compose_chat_v1_n4096_smoke` HARD_FAIL completed. Drill found a REAL mechanism bug independent of the parent finding's power-bound diagnosis: v1 had NO entity-alignment layer across per-KG bipolar codebooks (each `KGStore.__init__` regenerates random `E`, so the same entity is orthogonal across stores). Proposed arm_B alignment+chain via existing `char_trigram_encoder` is dispatch-ready, GATED on parent finding's per-corpus single-arm signal threshold.
**Pause state.** Honors `data/orchestrator_paused.flag`. If paused, file only; do not ship.
**Cite.** `notes/research_5x_deeper_cross_corpus_composition_gap_2026-06-23.md` (parent research note; pre-reg bands + HARD_PASS/HARD_FAIL thresholds verbatim).
**Discipline.** Per [[feedback-no-experiment-design-in-prompts]] — this handoff names anchor candidates + pointers, not implementations.

---

## Anchor candidates (rank-ordered, highest-leverage first)

### Anchor 1: `cross_corpus_compose_aligned_chain_v2_smoke` (CONDITIONAL DISPATCH)

**Anchor pointer.** `notes/research_5x_deeper_cross_corpus_composition_gap_2026-06-23.md` section (b)+(c); parent data `data/exp_cross_corpus_compose_chat_v1_n4096_smoke/metrics.json` (v1 HARD_FAIL detail).

**Substrate-product reading.** Cross-KG QA at the UI layer — V2/V3 enabler explicitly named by Strategy. With the alignment+chain operator, substrate can answer queries like "Who is the spouse of the director of Doctor Strange?" by chaining a HotpotQA hop (director-of) with an FB15k hop (spouse-of), bridged at the entity-name layer via trigram-encoded hub-vectors. Without this, the three substrate-native KG backends remain siloed and the multi-KG product capability stays dead.

**Tier hint.** Three-arm smoke at N_DIM=4096; n=100 bridge queries (~10min CPU). Reuses existing primitives entirely — no new code beyond a ~80-line `cross_kg_align.py` glue module bound to `char_trigram_encoder.nearest` + per-KG `KGStore.predict_one_hop_topk`. Bridge-query set construction (~30min, see parent note section (b)) is the load-bearing setup work.

**Why-now.** Drill identified a real mechanism bug v1 missed (no alignment layer) on top of the parent finding's power-bound diagnosis. The mechanism fix is mechanically cheap (existing primitives only), the test is discriminating (3 arms cleanly separate composition-works / v1-framing-was-right / fundamentally-broken), and even a HARD_FAIL validates parent finding at the operator level rather than just the corpus-size level. P_revival = 0.30 conditional on gate (deflated from 0.45 raw per calibration-penalty discipline; capped at novel-synthesis ceiling 0.50 minus 0.20 for absent direct precedent on cross-KG chained retrieval with bipolar codebooks).

**PRE-FLIGHT GATE (load-bearing; do NOT dispatch arm_B until gate passes).** Run cheap per-corpus single-arm acc check on a 50-query bridge subset BEFORE arm_B dispatch. **Gate condition: at least 2 of {conceptnet, hotpotqa, fb15k} must hit single-arm em >= 0.10.** Currently only conceptnet meets this (v1 smoke: conceptnet=0.167, hotpotqa=0.000, fb15k=0.000). **Most likely outcome (~70%): gate FAILS, answer becomes FIX SINGLE-ARM FIRST, arm_B not dispatched, drill's load-bearing finding becomes the gate itself.**

**HARD_PASS thresholds (verbatim from parent §(c), BOTH required).**
1. arm_B em >= max(arm_A_per_corpus) + 0.10 at n=100.
2. arm_B em > arm_C em + 0.05 at n=100.

**HARD_FAIL thresholds (ANY).**
1. arm_B em < max(arm_A_per_corpus) — 0.02 (composition HURTS or noise-tie).
2. arm_B em < arm_C em — 0.02 (alignment+chain LOSES to v1 union-hub framing).
3. Pre-flight gate fails (no 2 corpora at single-arm>=0.10).

**Cost.** Gate-check: ~3min CPU (uses existing v1 smoke caches). arm_B smoke if gate passes: ~10min CPU at N_DIM=4096, n=100.

---

## Parked anchors (do NOT dispatch)

### `cross_corpus_compose_chat_v1_n4096` (already PARKed by parent)
**Park reason.** Power-bound + per-corpus saturation (per parent finding). THIS drill identified an additional mechanism gap; both gates must lift to revive — see Anchor 1 conditional dispatch.

---

## Context pointers (NOT summaries)

- Parent research note (full mechanism diagnosis + HARD_PASS/HARD_FAIL + calibration penalty): `d:/AI/hd-instrument/notes/research_5x_deeper_cross_corpus_composition_gap_2026-06-23.md`
- Predecessor research note (power-bound diagnosis): `d:/AI/hd-instrument/notes/research_2x_revival_overnight_negatives_2026-06-23.md`
- v1 cell failure metrics: `d:/AI/hd-instrument/data/exp_cross_corpus_compose_chat_v1_n4096_smoke/metrics.json`
- Per-KG cache files (load-bearing — gate-check reads these directly):
  - `d:/AI/hd-instrument/data/conceptnet_100k_chat_cache.pkl`
  - `d:/AI/hd-instrument/data/hotpotqa_chat_cache.pkl`
  - `d:/AI/hd-instrument/data/fb15k_237_chat_cache.pkl`
- Substrate primitives (composes with arm_B):
  - `d:/AI/hd-instrument/hdlab/kg_traversal.py` — KGStore + predict_one_hop_topk (line 91)
  - `d:/AI/hd-instrument/hdlab/multi_hop.py` — naive_chain + iter_cleanup_chain (line 36, 55)
  - `d:/AI/hd-instrument/hdlab/char_trigram_encoder.py` — CharTrigramEncoder.encode + nearest (line 84, 112)
- Composes-with dashboard chat path: `d:/AI/hd-instrument/tools/dashboard/server.py:substrate_native_query_response` (intent-routing for cross-corpus queries once arm_B ratifies).

---

## Contract

This handoff is dispatch-ready for exp_dev IF AND ONLY IF the pre-flight gate is passed. If gate fails, the correct action is to mark the cell `DEFERRED_POWER_GATE + MECHANISM_GAP_IDENTIFIED` in cap_map and route to per-corpus capacity work (encoder-side cleanup ceiling-break already in flight per `notes/research_encoder_side_cleanup_ceiling_break_2026-06-23.md`).

exp_dev autonomy: implementation of `cross_kg_align.py`, bridge-query set construction, and 3-arm smoke harness are exp_dev's call. Research has named only the operator (alignment+chain via trigram hub), the gate (per-corpus >=0.10), and the pre-reg bands (HARD_PASS/HARD_FAIL verbatim above).

## Autonomy declaration

- Bridge-query set construction (which template families, gold-answer source): exp_dev's call. Suggested split (40/30/30 HotpotQA→FB15k / HotpotQA→ConceptNet / FB15k→ConceptNet) from parent note §(b) is a sketch, not a prescription.
- N_DIM choice for arm_B smoke: N_DIM=4096 default per parent; exp_dev may smoke at N_DIM=2048 if compute-tight, but production cell must match 584/585/588 chain-grade configs.
- Whether to ship arm_B at all if gate passes: exp_dev's call given budget. If passes but exp_dev judges other anchors higher-leverage, file as queued not parked.
