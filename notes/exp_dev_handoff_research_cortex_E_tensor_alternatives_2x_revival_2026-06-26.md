# exp_dev hand-off -- research: cortex E_tensor alternatives 2x revival drill (beyond existing 4x)

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** Cortex E_tensor HARDER_REGIME HARD_FAIL wrong-direction + Wave 1.6 RETEST in-flight contingency planning; research note `notes/research_cortex_E_tensor_wrong_direction_2x_revival_drill_2026-06-26.md`
**Pause state:** check `data/orchestrator_paused.flag` before dispatch; if present, this handoff queues but does not ship.
**Wave 1.6 RETEST status:** in flight per USER fairness fixes. **DO NOT dispatch these anchors until Wave 1.6 RETEST verdict is in** -- if RETEST HARD_PASS, these anchors are NOT needed; if RETEST HARD_FAIL or HARD_FAIL_FAIRNESS, these anchors become the next-line mechanism alternatives.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M_OLD, M_RECENT, J, e/h-thresholds, seed count, threshold bands, queue choice, ETA, smoke profile, FULL profile, anchor naming. Research provides mechanism design + pre-reg suggestion + cross-discipline grounding; exp_dev provides the cell.

---

## Anchor candidates (rank-ordered; contingent on Wave 1.6 RETEST HARD_FAIL)

### ANCHOR 5 (TOP PRIORITY): edge_importance_bound_pair_consolidation_v1

- **Anchor pointer:** `notes/research_cortex_E_tensor_wrong_direction_2x_revival_drill_2026-06-26.md` Section "ANCHOR 5".
- **Substrate-product reading:** moves importance signal from per-atom-scalar SPACE (which inherits magnitude correlation) to per-EDGE space (graph centrality over bound-pair structure). Atom importance is DERIVED from sum-of-edge-importance, not from retrieval frequency. The fairness check `cor(E_derived, |W|) < 0.30` should PASS by structural orthogonality. Brain-grounded (Govindarajan-Israely-Tonegawa clustered synaptic plasticity). Math-grounded (Brin-Page PageRank centrality). Network-science-grounded (Seidman k-core decomposition).
- **Substrate primitives needed:** existing binding.py (HRR role-filler bind/unbind) + NEW `hdlab/edge_importance.py` (sparse H[i,j] dict, increment on composite query, derived E from row-sum or PageRank, downscale gate).
- **REQUIRES composite-query workload:** the substrate's current cortex cells use mostly single-atom queries. Anchor 5 cell MUST include composite-query generation (bind atom pairs into a query, retrieve composite result, decompose). exp_dev: budget extra cell-author time for this setup (~2 hr).
- **Tier hint:** likely Tier B local_cpu (~4-6 CPU-hr including composite-query setup).
- **Why first:** structurally orthogonal to magnitude (the load-bearing fairness check the prior cells failed); strong brain + math + network-science grounding; unblocks USER pivot toward "compositional understanding first."

### ANCHOR 6: external_homeostatic_target_set_point_v1

- **Anchor pointer:** `notes/research_cortex_E_tensor_wrong_direction_2x_revival_drill_2026-06-26.md` Section "ANCHOR 6".
- **Substrate-product reading:** removes per-atom importance entirely; replaces with a SHAPE INVARIANT (target lognormal distribution for W-norms, per Buzsaki-Mizuseki 2014 cortical lognormality). Downscale rule is statistical distribution-matching, not retrieval-derived. The fairness check REFRAMES to `KL(post_W, target) < KL(pre_W, target)` because there is no per-atom importance to test orthogonality on. Brain-grounded (cortical lognormality). Math-grounded (max-entropy under moment constraints). Stat-mech-grounded (Boltzmann distribution maintenance under detailed balance). Signal-processing-grounded (mu-law companding).
- **Substrate primitives needed:** existing cleanup_memory.py + NEW `hdlab/distribution_homeostasis.py` (fit current W-norm distribution, compute KL to target lognormal, identify outlier-tail atoms, schedule downscale).
- **REQUIRES USER reframe of fairness check:** the original USER fairness gate `cor(E, |W|) < 0.30` does NOT apply to distribution-matching mechanisms. Anchor 6 needs a different pre-reg gate (KL-improvement). exp_dev should surface this in pre-reg authoring; if USER rejects the reframe, Anchor 6 is non-applicable.
- **Tier hint:** Tier B local_cpu (~3-5 CPU-hr; single primitive + distribution-fit cell).
- **Why second:** structurally novel mechanism class (no per-atom importance signal at all); brain-grounded; lower P due to pre-reg reframe risk; would close the cortex-content-extraction problem if it works.

---

## Context pointers (file paths; not summaries)

- `notes/research_cortex_E_tensor_wrong_direction_2x_revival_drill_2026-06-26.md` -- full research drill with mechanism specs + falsifiable predictions
- `notes/research_cortex_4x_cross_discipline_selective_abstraction_2026-06-26.md` -- existing 4x drill; ANCHORS 1-4 cover excitability / ultrametric / SOC / MDL. The 2 anchors in THIS handoff are DIFFERENT mechanism classes (edge-space + distribution-space).
- `notes/exp_dev_to_research_cortex_E_tensor_v2_SMOKE_HARD_FAIL_Fix_B_wrong_shaped_2026-06-26.md` -- exp_dev's prior diagnosis of why per-atom E inherits magnitude correlation; 3 probe candidates listed there (counterfactual-utility / surprisal-weighted / random-projection) are DIFFERENT from the 2 anchors in THIS handoff
- `data/exp_cortex_E_tensor_HARDER_REGIME_v1_smoke/metrics.json` -- HARDER_REGIME failure (gap_E_vs_RND=-0.217)
- `data/exp_cortex_E_tensor_RETEST_fairness_v2_smoke/metrics.json` -- RETEST v2 failure (cor=0.984)
- `preregs/2026-06-26_cortex_E_tensor_RETEST_fairness_v2.md` -- existing pre-reg with `cor < 0.30` fairness gate (load-bearing for Anchor 5; reframe required for Anchor 6)
- `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md` -- USER pivot; cells must NOT use language eval as success criterion

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke. Anchor 5 inherits the USER cor<0.30 fairness check; Anchor 6 REQUIRES a reframe to KL-improvement (surface to USER if exp_dev cannot ratify the reframe under existing standing rules).
- Self-test per [[feedback-formula-selftests]]: Anchor 5 unit test for H[i,j] increments on composite queries + PageRank convergence on small synthetic graph; Anchor 6 unit test for KL improvement on a controlled distribution shift.
- Multi-seed FULL on smoke clearance; minimum 3 seeds.
- Smoke MUST use the same HARDER_REGIME parameters as `cortex_E_tensor_HARDER_REGIME_v1` (N=256, M_OLD=200, M_RECENT=150, J=1000) for direct comparability.
- STOP at smoke per USER pre-reg gate ("if fairness checks still fail at smoke, STOP and route back to research").
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code per [[feedback-ship-name-collision]].
- status_log entry per anchor with `plain_language` + `importance`.
- Fix #26 predispatch_check on each anchor name before authoring.

## Autonomy declaration

exp_dev decides ALL of: anchor name, N, M_OLD, M_RECENT, J, e/h-thresholds, seed count, threshold bands, queue choice, ETA, smoke profile, FULL profile, integration approach. If exp_dev wants to drop one anchor and substitute a different mechanism (e.g., a hybrid of Anchor 5 + 4x-drill Anchor 2 ultrametric clustering), that is exp_dev's call.

**Wave 1.6 RETEST contingency:** if Wave 1.6 RETEST verdict is HARD_PASS, do NOT dispatch these anchors -- mark this handoff superseded. If Wave 1.6 RETEST is MIDDLE_BAND or HARD_FAIL_FAIRNESS, dispatch Anchor 5 first (Anchor 6 contingent on USER pre-reg reframe).

---

## Filed by

Research (Opus 4.7 1M), 2026-06-26, in response to USER 2026-06-26 "drill negatives 2x" directive on cortex E_tensor HARDER_REGIME HARD_FAIL wrong-direction.
