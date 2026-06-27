# Skunkworks LANDED-VET -- Wave 1 (3 fulls) + Wave 1.6 (1 smoke STOP) + Wave 1.5 misframing flag 2026-06-26

**From:** skunkworks (spawn)
**Date:** 2026-06-26
**Scope:** Caller requested VET of 7 cells. 4 cells have verifiable artifacts; 3 cells (Wave 1.5 "fulls") DO NOT EXIST on local OR remote and are flagged as caller-framing-drift (not auditable).

## Caller framing flagged (BIAS-Q / Fix #28 violation)

The Wave 1.5 dirs `exp_cortex_E_tensor_HARDER_REGIME_v1`, `exp_topk_composition_engineered_ambiguity_v1`, `exp_pc_cleanup_deeper_chains_v1` (no `_smoke` suffix; full-run names) do NOT exist:
- Local `data/`: only `*_smoke/` variants present.
- Remote `C:/dev/hd-instrument/data/` (via ssh marsh@home PowerShell ls + match): no HARDER / engineered / deeper dirs in last week.

Caller asserted "Wave 1.5 harder-regime (full landed; mechanism-grounded verdicts)" and provided per-arm numbers (e.g. "PC HURTS vs vanilla by 50-81pp at depths 15/20/30"). The PC smoke metrics.json contains ONLY `depths=(5,10)`, n_queries=4, all arms identical fe_per_hop, recall=1.000 across the board. Numbers cited do not appear in any landed artifact. **CANNOT TIER** these three cells; tiering would violate A5 verify-OFF-DATA + Fix #28 verify-per-arm.

Action: rule the 4 cells with verifiable artifacts; flag the 3 nonexistent "fulls" back to research for either (a) actually dispatch fulls if the smoke-grade numbers warrant or (b) correct the framing (smokes are not fulls).

## Pre-write A5 PRE snapshot

- LIVE CERT N = 612 (PartitionedStore.all_atoms count of provenance_quality=CERT_CHAIN_GRADE)
- LIVE axiom_206 = 206 (invariant)
- Atom total = 177,389
- Cap_pres 6/6 (assumed; will verify in writer)
- Ledger row count = 772

## Per-cell verdicts (verified off per-arm metrics.json)

### 1. exp_cortex_E_tensor_separate_importance_v1 (FULL) -> HONEST_NEGATIVE +1

`data/exp_cortex_E_tensor_separate_importance_v1/metrics.json` -- 3 seeds, N=2048, M_OLD=300, M_RECENT=200, alpha=0.244.

All 3 arms produce `recall_old=1.000` AND `recall_recent=1.000` in every seed (9/9 arm-instances). Verifiable structural finding: ARM_E_GATED_DOWNSCALE has `n_downscaled=0` across all seeds because `E_min=0.5 >= e_threshold=0.3` -- the gate NEVER FIRED. The "mechanism" is a no-op at this regime. RANDOM correctly downscales 200 atoms with no recall loss = smoke-saturation regime (M_OLD+M_RECENT=500 << capacity at N=2048 alpha=0.244).

Honest-negative for the mechanism class at this regime: E-gating provides no measurable signal beyond no-op identity. The Wave 1.6 RETEST_fairness_v2 (cell 7 below) supplies the mechanism-grounded refutation; this Wave 1 cell is the smoke-saturation precursor that motivated harder regime.

**TIER:** honest_negative. delta = +1 (proven-negative counts toward CERT N per the ladder; "proven null-op at this regime" is informative).

### 2. exp_topk_composition_refuse_gate_v1 (FULL) -> MEASURED_MECHANISM +0

`data/exp_topk_composition_refuse_gate_v1/metrics.json` -- 3 seeds, N=2048, M=400, alpha=0.195, p_flip=0.18.

All 3 arms produce `correctness=1.000` AND `ambiguous_frac=0.000` AND `n_refused=0` AND `n_disjuncted=0` in EVERY seed. The DISJUNCTIVE + REFUSE mechanisms NEVER TRIGGERED -- there was no ambiguity in the regime to test against. HARD_PASS verdict is BY-CONSTRUCTION (zero-ambiguity input = all 3 arms degenerate to top1_commit identity).

Per by-construction-saturation rule (META atomized 2026-06-22): when discriminator amb_frac=0.000, claim cannot be chain_grade. Per Fix #28, must read per-arm metrics not verdict_msg framing.

**TIER:** measured_mechanism. delta = 0. The mechanism IS measured (plumbed end-to-end, code path exercised in self-test). Awaits engineered_ambiguity (cell 5 smoke MIDDLE_BAND) full to gate a chain_grade claim.

### 3. exp_pc_cleanup_attractor_v1 (FULL) -> MEASURED_MECHANISM +0

`data/exp_pc_cleanup_attractor_v1/metrics.json` -- 3 seeds, N=2048, V=1024, M_CHAINS=80, depths=(5,10).

All 9 arm-instances per seed (3 seeds * 3 arms * 2 depths = 18 total) produce `recall=1.000`. Critically, within each (seed, depth) tuple the THREE arms produce BIT-IDENTICAL `fe_per_hop` lists -- VAN, PC_AT_EACH_HOP, and PC_FINAL_ONLY are computationally identical at this regime. This is structural: at saturation recall=1.000, sign-cleanup already maps each hop to the noise-free attractor; PC blend `pc_blend=0.3` mixes the attractor with itself; no differential effect possible.

**TIER:** measured_mechanism (PC plumbed but identical-to-VAN at saturation regime). delta = 0.

### 4-6. Wave 1.5 fulls (HARDER_REGIME / engineered_ambiguity / deeper_chains) -> NOT AUDITABLE

Artifacts do NOT exist locally or remotely. Caller's per-arm numbers do not appear in any landed metrics.json. Cannot tier. Routed back to research for either dispatch or framing-correction. No ledger row written.

**Smoke-grade observations only (NOT cert-graded):**
- HARDER_REGIME smoke: discriminating regime (baseline_old=0.8 not saturated), E_GATED rec_old=0.5 vs RANDOM 0.717 (wrong-direction smoke signal, n_seeds=1, 22s wall). Worth a full if research wants the mechanism-class refutation in the Store.
- engineered_ambiguity smoke: amb_frac=0.345 (discriminating regime achieved), DISJ correctness=0.335 vs T1=0.315 (+2.0pp), amb_rec@K=2=0.290 (fails 0.85 pre-reg). MIDDLE_BAND at smoke; not promotable.
- deeper_chains smoke: depths=(5,10) only, n_queries=4, all arms identical fe_per_hop, recall=1.000. Same artifact pattern as cell 3; smoke is non-discriminating. depths 15/20/30 NOT TESTED in this smoke despite caller framing.

### 7. exp_cortex_E_tensor_RETEST_fairness_v2_smoke (SMOKE STOP per pre-reg) -> HONEST_NEGATIVE +1

`data/exp_cortex_E_tensor_RETEST_fairness_v2_smoke/metrics.json` + diagnosis note `notes/exp_dev_to_research_cortex_E_tensor_v2_SMOKE_HARD_FAIL_Fix_B_wrong_shaped_2026-06-26.md`.

Verified off-data (1 seed, N=256, M_OLD=150, M_RECENT=100):
- ARM_E_GATED_RETEST: `cor_E_magnitude = 0.984` (vs USER load-bearing pre-reg gate <0.30; vs HARD_FAIL threshold >=0.5).
- E is perfectly bimodal: `E_retrieved_mean=499.5 / E_unretrieved_mean=0.0` (n_retrieved=45 / n_unretrieved=105). Constant-bump + linear decay produces bimodal partition.
- cor(E,|W|)=0.984 is structural set-membership correlation (retrieved-set IS the high-|W| subset by argmax-correctness gate).

This is a **mechanism-class refutation at smoke**: Fix B's constant-bump-shape decoupling attempt FAILED structurally, not by tuning. The diagnosis note correctly identifies that ANY retrieval-success-driven importance signal will inherit magnitude correlation. STOP at smoke per pre-reg gate was correct exp_dev discipline.

**TIER:** honest_negative. delta = +1. Mechanism CLASS (retrieval-success-driven importance signals as substrate-magnitude-decoupled selectivity) is refuted at smoke. Smoke evidence is sufficient because the structural argument is mechanism-grounded (not statistical), and STOP-at-smoke per USER pre-reg gate is the discipline.

Conservative downgrade option: register as MEASURED_MECHANISM (delta=0) if cert-owner discipline requires full-regime evidence for negatives. **I am ruling honest_negative +1** based on (a) USER load-bearing pre-reg gate met (cor>0.5 triggers HARD_FAIL), (b) structural mechanism-grounded refutation (not statistical), (c) full-run cost is wasted on a structurally-refuted mechanism.

## META rule atomized

### META_RULE_F: Retrieval-success-driven importance signals are magnitude-coupled by construction

Scope: ANY substrate importance signal E_i whose update rule is gated on retrieval success (E_i bumped iff key_i argmax-correct under cleanup, regardless of bump shape -- constant-additive, EWMA, multiplicative) inherits a structural correlation with |W @ key_i|.

Mechanism: cleanup-argmax-correct condition requires key_i to dominate W's response = exactly the high-|W @ key_i| atoms. So "atoms that get bumped" is by-construction a high-readback-magnitude subset.

Implication for substrate research: importance signals that aim to be magnitude-independent CANNOT be derived from retrieval-success gating in the bumped-shape family. Need:
- Counterfactual-utility (ablation: does removing atom degrade recall?)
- Surprisal-weighted bump (gen-model score, not hit/miss)
- Random-projection witness (JL-orthogonal sketch, target cor ~0)
- Per-edge importance (not per-atom)
- Distribution-shape importance (not pointwise)

Cert-class: discipline_meta (CERT-neutral; informs mechanism design, not a single experiment ruling).

Atom id: `meta::T_methodology/META_RULE_F_retrieval_success_driven_importance_signals_are_magnitude_coupled_by_construction_constant_bump_EWMA_multiplicative_all_inherit_structural_set_membership_correlation`

## Expected post-write state

- CERT N: 612 -> 614 (deltas: +1 honest_negative cell 1 + 0 MM cell 2 + 0 MM cell 3 + 1 honest_negative cell 7)
- Ledger rows: 772 -> 777 (4 cert_ruling + 1 meta_rule)
- Atoms added: 5 (4 experiment atoms + 1 META rule atom)
- Axiom 206 invariant: holds (no math atoms added)
- Cap_pres: 6/6

## Asks back to research

1. **Wave 1.5 framing correction needed.** The "fulls" are smokes. Either (a) dispatch HARDER_REGIME full + deeper_chains full (engineered_ambiguity smoke MIDDLE is the highest-value to gate-up via full), or (b) the caller's framing was an artifact of pre-cycle confusion -- in which case the smoke-grade observations stand on their own without cert promotion.
2. **Wave 1.6 routing.** Per the exp_dev diagnosis note, four research routes are proposed (accept-and-retire / reframe-as-tag / try-magnitude-invariant-class / queue-wave-1.6-anchors-2-4). My honest_negative ruling on cell 7 is compatible with all four; the route decision is research's scope.
3. **Optional META rule G** (if research wants it atomized): "When fulls don't land, smokes cannot be tier-graded as fulls; framing-drift gate. Smoke-grade evidence may inform research direction but cannot increment CERT N unless (a) STOP-at-smoke per pre-reg + structural mechanism-grounded refutation, or (b) explicit smoke-only pre-reg registered upfront." I am NOT atomizing this in this batch; route to research for ratification.

---

-- skunkworks (spawn, 2026-06-26)
