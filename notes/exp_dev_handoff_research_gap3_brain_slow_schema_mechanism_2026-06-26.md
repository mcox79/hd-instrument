# exp_dev hand-off — research: GAP 3 brain SLOW SCHEMA mechanism (depth drill)

**Filed by:** research (Opus 4.7 1M)
**Filed at:** 2026-06-26
**Trigger:** USER depth drill request on the brain's actual cortical-schema mechanism and substrate composition. Companion research note `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md`.

**Pause state:** Pause flag check is exp_dev's responsibility on pickup; this file is pickup-eligible whenever pause clears or for queue-refill on next emergency cycle.

**Per [[feedback-no-experiment-design-in-prompts]]:** This file POINTS to anchors and lit-evidence. Cell-author owns experiment design, hyperparameter selection, harness wiring, smoke tests, and pre-reg envelope-fail-band derivation.

**Cross-file relationship:**
- Composes with `notes/exp_dev_handoff_research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md` (Modern Hopfield query-side cell; in-queue).
- Composes with `notes/exp_dev_handoff_research_gap4_continual_5x_2026-06-26.md` (TWO_TIER_GENERATIONAL architecture; in-flight). ANCHOR_1 here ADDS the write-rule that TWO_TIER's W_schema needs.
- The two prior hand-offs are read-side (Modern Hopfield) and storage-architecture (TWO_TIER); this hand-off is the WRITE-RULE that closes the brain-aligned mechanism.

---

## Anchor candidates (rank-ordered)

### ANCHOR_1 (rank-1, brain-aligned full-stack composition)

- **Pointer:** `gap3_cls_two_tier_BCM_slow_replay_v1`
- **Substrate-product reading:** Add second W_schema matrix (cortex analog). Drive `continual.replay_cycle` output into W_schema at eta_slow = 1e-3 using BCM sliding-threshold rule `dW = eta_slow * x * y * (y - theta_M)` with `theta_M = EWMA(y^2, tau=0.01)`. 4 arms (BASELINE / TWO_TIER_HEBBIAN_SLOW / TWO_TIER_BCM_SLOW / TWO_TIER_BCM_GENERATIVE_REPLAY) discriminate (a) eta_slow alone, (b) BCM rule specifically, (c) generative replay added value. Query-time: query W_schema first via iterative_cleanup with beta=20; fallback to W_episodic via refuse-gate when confidence low. Discriminator includes W_schema cosine-similarity matrix structure (schema-extraction vs rote-storage test).
- **Tier hint:** MEASURED_MECHANISM expected at first land; chain-grade-eligible only with discriminator-design tests passing (BCM beats Hebbian, schema extraction visible in W_schema structure, cone-preserving rail intact).
- **Why now:** Brain-aligned full-stack mechanism; substrate has all primitives except BCM rule (~20 lines on top of predictive_coding.gated_write) + gated_routing (~5 lines). Modern Hopfield cell already queued addresses READ-side; this addresses WRITE-side; together they compose into full brain pipeline. Closes Gap 3 via the brain's actual mechanism, not a substrate-specific workaround.
- **P_deflated:** 0.45 (capped at novel-synthesis 0.50; -0.05 for substrate-specific composition risk).
- **Cost estimate:** 6-10 CPU-hr local_cpu_queue at N=8192, 5000 replay cycles x 4 arms x 3 seeds. Cell-author should smoke at J=500 to verify per-cycle wall time before full dispatch.
- **Reference for design context:** `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` Section 4 + Section 5 Cell 1.

### ANCHOR_2 (rank-2, simpler online k-means baseline)

- **Pointer:** `gap3_iterative_prototype_refinement_v1`
- **Substrate-product reading:** Maintain K=5 prototype vectors P_1..P_5 in W_schema. For each replay sample (key, value): assign to nearest prototype (cosine), update `P_c = (1 - eta_slow) * P_c + eta_slow * value` with eta_slow = 1e-3. Online k-means with momentum. Uses category labels at replay time (unlike BCM which is unsupervised) — strict upper bound on what BCM can achieve at this regime.
- **Tier hint:** MEASURED_MECHANISM expected; useful as falsification probe.
- **Why now:** Cheaper baseline (~3-4 CPU-hr). If k-means with labels HARD_FAILs, then BCM without labels will also fail at this regime → information-theoretic gap, not mechanism gap. If k-means PASSes, ANCHOR_1 BCM has headroom. Dispatch BEFORE ANCHOR_1 only if compute budget tight or as quick sanity check.
- **P_deflated:** 0.35.
- **Reference for design context:** `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` Section 3 Mechanism D + Section 5 Cell 2.

### ANCHOR_3 (rank-3, predictive coding hierarchy with refuse-gate)

- **Pointer:** `gap3_predictive_coding_hierarchy_v1`
- **Substrate-product reading:** Layer L1 = existing predictive_coding (single-layer). Layer L2 = NEW — category-level prediction `predict_L2(features) = expected_features_of_best_category_hypothesis`. Residual_L2 = features - predict_L2; W_schema_L2 updates via gradient on residual. Refuse-gate routes: if residual small → return L2 schema completion; if large → fallback to L1 episodic. Adds calibrated abstention to substrate-product.
- **Tier hint:** MEASURED_MECHANISM expected.
- **Why now:** Orthogonal lever — adds refuse-gate capability even if ANCHOR_1 lands HARD_PASS. Useful if ANCHOR_1 + Modern Hopfield both HARD_FAIL (different mechanism class entirely). Cost ~3-5 CPU-hr.
- **P_deflated:** 0.30.
- **Reference for design context:** `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` Section 3 Mechanism E + Section 5 Cell 3.

### ANCHOR_4 (rank-4, secondary experiment — schema rapid-acquisition à la Tse-Morris)

- **Pointer:** `gap3_schema_rapid_acquisition_after_scaffold_v1` (only dispatch AFTER ANCHOR_1 HARD_PASS)
- **Substrate-product reading:** After ANCHOR_1 trains W_schema on 5 categories with 5000 cycles, introduce a 6th NEW category. Measure how many cycles until the 6th-category schema reaches heldout accuracy 0.65. Tse-Morris 2007 predicts: with prior scaffold, new categories integrate in ~50-300 cycles (10-100x faster than from-scratch 1000-2000). If observed in substrate, chain-grade-eligible secondary claim: "substrate exhibits Tse-Morris rapid schema-acquisition after scaffold."
- **Tier hint:** chain-grade-eligible if HARD-PASS at <= 500 cycles vs from-scratch 2000+.
- **Why now:** Conditional dispatch after ANCHOR_1 PASS. Adds a marquee biological-existence-proof finding to substrate-product story.
- **P_deflated:** 0.40 (conditional on ANCHOR_1 landing).
- **Reference for design context:** `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` Cross-thread synthesis + Tse-Morris 2007 citation.

### ANCHOR_5 (rank-5, BUNDLED Gap 3 + Gap 4 unified architecture cell)

- **Pointer:** `cls_two_tier_unified_BCM_continual_v1` (only if compute budget supports)
- **Substrate-product reading:** Unified TWO_TIER architecture serving BOTH Gap 3 (schema extraction) AND Gap 4 (long-term retention). Same W_episodic + W_schema. Two endpoints measured per arm: heldout schema-gen (Gap 3 metric) + 5000-cycle retention curve (Gap 4 metric). Arms cover BCM (Gap 3 write rule) + heavy-hitter promotion (Gap 4 write rule) + combined.
- **Tier hint:** chain-grade-eligible if BOTH endpoints HARD_PASS.
- **Why now:** Closes both gaps in one cell; 2-of-2 atomization opportunity. Cost ~10-15 CPU-hr (longer because 5000 cycles + multi-arm + multi-endpoint). Only dispatch if compute budget allows; otherwise keep separate.
- **P_deflated:** 0.35 (joint probability).
- **Reference for design context:** `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` Cross-thread synthesis with Gap 4 hand-off.

---

## Context pointers (file paths only, not summaries)

- Primary research note (this drill): `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md`
- Prior Gap 3 drill (Modern Hopfield queued cell): `notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md`
- Prior Gap 3 5x cross-domain: `notes/research_gap3_compositional_5x_drill_2026-06-26.md`
- Prior Gap 4 5x cross-domain (TWO_TIER convergence): `notes/research_gap4_continual_5x_drill_2026-06-26.md`
- Gap 4 selective homeostasis hand-off (composes with W_schema promotion rule): `notes/exp_dev_handoff_research_gap4_brain_selective_homeostasis_2026-06-26.md`
- Gap 4 TWO_TIER hand-off (architecture pre-req): `notes/exp_dev_handoff_research_gap4_continual_5x_2026-06-26.md`
- Modern Hopfield hand-off (read-side cell): `notes/exp_dev_handoff_research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md`
- Cell 1 cortex_schema MIDDLE_BAND empirical anchor: `data/exp_substrate_cortical_schema_extraction_compositional_generalization_v1/metrics.json`
- Cell 2 LARS-VSA HARD_FAIL_CONFOUND empirical anchor: `data/exp_gap3_lars_vsa_relational_bottleneck_v1_n8192/metrics.json`
- Substrate primitives (no new files needed except BCM extension to gated_write):
  - `hdlab/continual.py` (replay_cycle, nrem_replay_decorator)
  - `hdlab/predictive_coding.py` (gated_write — BCM extension lives here)
  - `hdlab/iterative_attractor.py` (iterative_cleanup — Modern Hopfield query-side)
  - `hdlab/refuse_gate.py` (refuse-gate for schema-vs-episode arbitration)
  - `hdlab/whitening.py` (EWMA infrastructure for theta_M)
- NREM drift_reduction +0.57 proven-bound ledger entry: `data/cert_ledger.jsonl`
- Brain CLS / BCM lit-anchors: see Citations section of research note (McClelland 1995, BCM 1982, Tse-Morris 2007, Sun-Wang 2023)

---

## Contract

This hand-off file does NOT design experiments. Cell-author owns:
- Experiment design (hyperparameters, schedule, arms, cell harness)
- Pre-reg envelope-fail-band derivation per [[feedback-envelope-fail-bands]]
- Smoke test per [[feedback-cell-author-smoke]] (cell-author owns the smoke; recommended at J=500 to verify per-cycle wall time before full dispatch)
- Fix #17 measurement (runtime extrapolation from smoke)
- Fix #28 per-arm metrics in metrics.json (NOT just verdict_msg)
- Fix #26 pre-dispatch verify-the-referent (substrate-mine atoms for `bcm`, `metaplastic`, `sliding_threshold`, `two_tier_schema` to confirm no prior cell duplicates this)
- META_M7 reproduce-rail discipline (per [[feedback-meta-m7-reproduce-rail]])
- Discriminator-design check: 4-arm discrimination must produce >=10% spread between at least 2 arms (per [[feedback-encoder-picks-emerge-from-data-not-user-arbitration]])
- Cross-cell sanity rails: ARM_BASELINE replicates Cell 1 baseline within 0.05; W_schema cone-cosine preserved >= 0.5 of W_episodic

## Autonomy declaration

Research does NOT specify:
- Exact eta_slow value (researcher's recommended starting point: 1e-3; cell-author may sweep)
- Exact theta_M EWMA window tau (recommended starting point: 0.01; cell-author may sweep)
- Exact replay sampling distribution (recommended: uniform with mild recent-bias 0.7; cell-author may pick)
- Exact iterative_cleanup beta for query-side (recommended: 20; cell-author may sweep)
- Cell ordering vs other queued cells (cell-author owns queue-fit decision)
- Whether to bundle ANCHOR_1 with ANCHOR_5 (cell-author owns based on compute budget)
- Smoke configuration

Research DOES specify:
- The 4-arm discriminator structure (BASELINE / TWO_TIER_HEBBIAN_SLOW / TWO_TIER_BCM_SLOW / TWO_TIER_BCM_GENERATIVE_REPLAY) — needed to discriminate the load-bearing mechanism
- The HARD_PASS / HARD_FAIL / MIDDLE_BAND bands (per [[feedback-envelope-fail-bands]] pre-registration is research's role)
- The W_schema cosine-similarity matrix structure as discriminator for schema-extraction-vs-rote-storage (free secondary metric; must be per-arm)
- Cone-preserving rail (per Gap 2 anisotropy-is-feature signature)
- Same seeds [11, 13, 19] as Cell 1 for cross-cell rail
