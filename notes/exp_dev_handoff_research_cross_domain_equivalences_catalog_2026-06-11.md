# exp_dev hand-off — research: cross-domain equivalences catalog

Filed-by: research (Opus)
Date: 2026-06-11
Trigger: research delivery `notes/research_drill_cross_domain_equivalences_catalog_2x_2026-06-11.md` enumerated 42 EQUIVALENT_UNDER edges and surfaced one substrate-novel exp_dev-actionable anchor (softmax-resonator).
Pause state: respect `data/orchestrator_paused.flag` if present; this hand-off is annotation-only until exp_dev confirms pipeline state.

Per [[feedback-no-experiment-design-in-prompts]]: this file lists anchor candidates with substrate-product reading and pointers ONLY. exp_dev owns the experimental design, smoke gate, and HP/HF threshold pre-registration.

---

## Anchor candidates (rank-ordered)

### Anchor 1 — substrate-self-index equivalence-graph ingest smoke (Tier A)

- **Anchor pointer:** new cell `substrate_self_index_equivalence_edge_ingest_smoke.py`
- **Substrate-product reading:** ingest the 42 cataloged equivalences as typed `EQUIVALENT_UNDER` edges with `under_transformation` (text) and `fidelity` (exact/approximate/probabilistic) fillers; run the decisive test from research note section (b) — 10 sampled cross-domain query pairs, measure 2-hop recall and emergent second-order paths.
- **Tier hint:** Tier A on first emergent second-order path; Tier B on >=8/10 direct-recall but no second-order; Tier C / HARD_FAIL on <5/10 (retire framing).
- **Why-now:** catalog is fresh, schema is concrete (3 fields per edge), substrate-self-index already has cross-domain equivalence relation type per prior strategy. CPU-cheap (~20 min).

### Anchor 2 — softmax-resonator variant (Tier B candidate)

- **Anchor pointer:** new cell `resonator_softmax_variant_smoke.py`
- **Substrate-product reading:** classical resonator network (Frady/Kent/Olshausen/Sommer 2020, arXiv:2007.03748) uses argmax over factor codebook per iteration; via semiring-shift equivalence #11 from the catalog (max-product <-> sum-product), a softmax-over-codebook variant exists and is **untested in published lit**. Hypothesis: softmax broadens basins of attraction in compositional cleanup, potentially rescuing some L6+ deep-binding cases currently outside resonator capacity.
- **Tier hint:** Tier B if softmax matches argmax baseline at moderate factor counts; Tier A if it strictly broadens basin (succeeds where argmax saturates).
- **Why-now:** sits on already-validated substrate primitives (FHRR cleanup); cheap to implement (~1 hr CPU); first novel-synthesis candidate from this research cycle.

### Anchor 3 — second-order equivalence path enumerator (deferred / supports Anchor 1)

- **Anchor pointer:** support cell for Anchor 1 — after ingest, run a transitivity sweep that composes pairs of `EQUIVALENT_UNDER` edges and reports candidate second-order equivalences ranked by substrate confidence.
- **Substrate-product reading:** the load-bearing product feature is **derived** equivalences (composing two stored edges). This anchor measures the emergent reasoning lift directly.
- **Tier hint:** depends on Anchor 1; do not ship independently.

---

## Context pointers (file paths, not summaries)

- `d:/AI/hd-instrument/notes/research_drill_cross_domain_equivalences_catalog_2x_2026-06-11.md` — full catalog with all 42 rows + fidelity tags + source anchors
- `d:/AI/hd-instrument/memory/substrate_v32_engineered_wrapper_2026-06-11.md` — current substrate framing (wrapper architecture)
- `d:/AI/hd-instrument/memory/substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md` — HMM-Viterbi precedent (catalog rows 5, 11, 20, 21 directly relevant)
- Frady et al 2020 resonator network: arXiv:2007.03748 (for Anchor 2 reference impl)
- `d:/AI/hd-instrument/notes/exp_dev_handoff_v195_pipeline_refill_2026-05-24.md` — structural template this hand-off follows

---

## Contract

This hand-off is annotation-only until exp_dev confirms pipeline state. No queue-add is requested from research. exp_dev decides whether to slot Anchor 1 or Anchor 2 (or neither) into the current cycle.

If pause flag is set: file is auto-discovered on the next refill cycle; do not act now.

## Autonomy declaration

exp_dev owns:
- experimental design and pre-registration bands
- smoke gate (composition-matched smoke + CI-band rule)
- HARD-PASS / HARD-FAIL thresholds
- queue lane choice (GPU vs home-CPU vs local-CPU)
- decision to defer either anchor if higher-priority work fills the cycle

research owns:
- the catalog itself (42 rows, fidelity tags, source anchors)
- the substrate-product reading for each anchor
- the cross-thread synthesis citing prior memory entries
- NOT the experimental design
