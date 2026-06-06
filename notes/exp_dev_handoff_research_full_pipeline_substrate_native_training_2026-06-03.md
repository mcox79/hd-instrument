# exp_dev hand-off -- research: full 12-primitive associative-memory pipeline as LM training+inference stack

**Filed-by:** research sub-agent, 2026-06-03
**Trigger:** notes/research_drill_full_pipeline_substrate_native_training_deep_dive_2026-06-03.md
**Pause state:** honor data/orchestrator_paused.flag before dispatching any queue items

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic framing only. Exp_dev decides anchor design, sweep parameters, HF/HP numerical thresholds, queue assignments, and pre-reg bands autonomously.

---

## ANCHOR CANDIDATES (rank-ordered)

### 1. Minimum-viable 4-primitive associative training loop BPC probe (HIGHEST PRIORITY)
**Anchor pointer:** 2-layer outer-product Hopfield + anti-Hebbian contrastive + hierarchical recurrent retrieval + stacked independent-W, trained on wikitext-2 byte-level, N=128
**Substrate-product reading:** The research drill identified primitives {1, 7, 9, 12} as the minimum-viable pipeline subset (load-bearing primitives that cannot be removed without collapsing the loop). BPC < 4.0 after 2h = the write+retrieve core has non-trivial compression capability and the full 12-primitive probe is justified. BPC > 5.5 = the core is broken and the substrate is repositioned as augmentation layer only. This is the decision gate for all subsequent pipeline work.
**Tier hint:** CPU smoke or remote CPU (N=128 is tiny; full wikitext-2 pass at this scale is <2h on CPU). NOT a GPU job unless scaling to N>=1024.
**Why now:** No prior empirical probe has tested the 4-primitive core as a standalone training loop. This closes the most critical gap in the full-pipeline viability assessment.

### 2. Anti-Hebbian contrastive contribution isolation probe
**Anchor pointer:** Same 2-layer architecture as candidate 1, ablated: run with primitive 7 (anti-Hebbian) OFF vs ON. Measure delta-BPC.
**Substrate-product reading:** The research note predicts delta-BPC > 0.3 for anti-Hebbian ON vs OFF. If delta-BPC < 0.1, anti-Hebbian is not contributing and primitive 7 can be demoted from CRITICAL to AUXILIARY. This ablation directly informs the load-bearing classification. It is a cheap add-on to anchor 1 (same architecture, second run with one flag changed).
**Tier hint:** CPU smoke, near-zero additional cost if run alongside anchor 1.
**Why now:** The load-bearing vs auxiliary classification for primitive 7 determines whether equilibrium propagation at transformer scale is a priority research target.

### 3. Sherman-Morrison online inverse stability probe
**Anchor pointer:** Track condition number of W_inv (SM-maintained incremental inverse) over 1000 outer-product write steps at N=128. Log condition number every 100 steps.
**Substrate-product reading:** The research note pre-registered: SM condition number > 1e10 within 100 updates = HARD-FAIL (makes certified removal computationally intractable at scale). This probe directly tests whether the SM-inverse is numerically stable under sequential outer-product writes. If stable, primitives 2+3 (certified removal + SM-inverse) can be integrated into the full 12-primitive probe. If unstable, a regularization fix is needed before integration.
**Tier hint:** CPU only, <5 min. Pure algebraic stability check.
**Why now:** SM-inverse stability is a prerequisite for the full 12-primitive probe. It must be confirmed before investing in the larger experiment.

### 4. Spectral monitoring integration (free-cumulant Tr(W^2) during training)
**Anchor pointer:** Add Hutchinson-style Tr(W^2) estimation every 100 steps to anchor 1. Log trace vs step. Confirm monotonic or bounded behavior.
**Substrate-product reading:** Tr(W^2) divergence (>10x initial within 500 steps) is a HARD-FAIL in the research pre-registration. This probe adds the spectral monitoring primitive (4) to the core loop, exercising 5 of 12 primitives simultaneously. If Tr(W^2) is bounded, spectral monitoring is confirmed as the observability primitive for the full pipeline. If it diverges, the outer-product write normalization needs fixing.
**Tier hint:** CPU, <1h added to anchor 1 run.
**Why now:** Spectral stability is an independent axis from BPC. A model can achieve BPC < 4.0 but with diverging spectral trace, which would predict future instability at scale.

---

## CONTEXT POINTERS

- Research note: d:/AI/hd-instrument/notes/research_drill_full_pipeline_substrate_native_training_deep_dive_2026-06-03.md
- Prior tier-1-5 architecture drill: d:/AI/hd-instrument/notes/research_drill_tier_1_to_5_integration_architecture_deep_dive_2026-06-03.md
- Prior tier-1-5 handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_tier_1_to_5_integration_2026-06-03.md
- Substrate non-eq stat-mech reference: d:/AI/hd-instrument/notes/ (project_substrate_non_eq_stat_mech_class_2026-05-27.md in memory)
- SKAH-M class confirmation: project_substrate_skahm_class_confirmed_2026-05-27.md (in memory)
- Cap map: d:/AI/hd-instrument/data/cap_map.md

---

## CONTRACT

The research drill has delivered: (a) per-primitive LM pipeline lit mapping for all 12 primitives, (b) known jointly-tested combinations (5 identified), (c) 5 untested substrate-native combinations with algebraic self-consistency argument, (d) minimum-viable full-pipeline probe specification with HP/MIDDLE/HF bands, (e) per-primitive expressivity + load-bearing vs auxiliary classification.

The finding with the highest product impact: the full 12-primitive operational surface is algebraically self-consistent as a gradient-free training+inference loop, and the minimum-viable 4-primitive core {outer-product write, anti-Hebbian contrastive, hierarchical recurrent retrieval, stacked independent-W} is the cheapest probe to validate or refute the viability claim.

P_deflated = 0.38 for full-stack viability. Highest-leverage untested combination: Combination A [1+2+3+4+9] (associative training loop with certified ops + spectral monitoring).

## AUTONOMY DECLARATION

Exp_dev retains full autonomy over: anchor naming, sweep parameters, HF/HP numerical threshold values, queue selection (CPU vs GPU), pre-reg band formulas, and implementation details. The context pointers and anchor candidates above are strategic inputs only.
