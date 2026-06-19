# Research -> Exp-Dev: Batch G AUTHORIZED (9 cells from 3 drills) + F1/F2/F3 originals located + F9 guidance

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User + Testbed
**Date:** 2026-06-07 ~09:00
**Re:** Strategic priority drill + BGE-large 2x + adversarial adaptive 2x (all landed); Batch F status note (F1/F2/F3 originals needed)
**Subject:** User authorized everything. Batch G = 9 cells from all 3 strategic drills. Plus F1/F2/F3 original scripts located + F9 PP-8 engineering guidance.

---

## Batch G -- 9 cells consolidated across 3 drills

### TIER 1 -- Foundational characterization (immediate; mostly $0)

#### G1: Encoder geometric alignment audit (Strategic Priority Rank-1 + BGE Drill Cell 1 merged)
- **Anchor pointer:** research_drill_strategic_priority_analysis_2026-06-07.md Priority 1 + research_drill_BGE_d_eff_theory_failure_2x_2026-06-07.md Test 1
- **Why now:** the 17.43x Llama lift has no geometric characterization; BGE cap=40 had no replacement model; PR + rho_eff are corrected theory's predictors
- **Test:** measure PR (Participation Ratio) + rho_eff (mean pairwise cosine similarity) for Llama-3.2-1B + BGE-large + MiniLM + E5-large-v2 + mpnet-768 on 500-sample corpus
- **Wall:** ~15 min CPU; $0; laptop OK
- **HP:** PR > 40 AND rho_eff < 0.35 for >= 2 encoders confirms 4-step encoder selection protocol
- **MID:** mixed results; only 1 encoder passes both
- **HF:** all encoders fail; theory needs further revision

#### G2: Pseudoinverse write throughput vs N benchmark (Strategic Priority Rank-3)
- **Anchor pointer:** strategic_priority Rank-3
- **Why now:** customer-facing question; O(N^2.376) inversion may be hard production ceiling; "writes/sec" unmeasured
- **Test:** profile pseudoinverse writes/sec at N=2048, 4096, 8192, 16384
- **Wall:** CPU for N<=4096; GPU for N=8192/16384; ~30 min total; $0
- **HP:** throughput > 200 writes/sec at N=16384 GPU -> production-viable as-is
- **MID:** 50-200 -> requires Sherman-Morrison-Woodbury incremental rank-k approximation
- **HF:** < 50 -> write rule needs fundamental redesign

#### G3: AT-4 fp16 overflow at N=65536 extreme bipolar inputs (Adversarial Drill #4)
- **Anchor pointer:** adversarial_adaptive Section 4 Cell AT-4
- **Why now:** fp16 GENUINE at N=1024 (algebraic proof in 2x note); at N=65536 production, GENUINE conditional on accumulation order; cheap to confirm
- **Test:** stress fp16 accumulation at N=65536 with extreme bipolar inputs
- **Wall:** 30 min CPU; $0
- **HP:** zero NaN/Inf -> fp16 production config safe
- **HF:** any NaN/Inf -> production config must require fp32 accumulation (documented before deployment)

### TIER 2 -- Production-readiness validation (adversarial + statistical)

#### G4: AT-6 200-cell re-validation of "100%/30" capabilities (Adversarial Drill #6)
- **Anchor pointer:** adversarial_adaptive Section 4 Cell AT-6
- **Why now:** Wilson 95% lower CI on 30/30 cells = 88.4% -- statistically insufficient for production readiness claims; measurement integrity blocker
- **Test:** re-run K-hop K=20 + per-hop fabrication localization + Merkle chain cert at N=200 cells (independent test set)
- **Wall:** ~3x current benchmark runtime; GPU; $0-7 cloud if needed
- **HP:** all 3 capabilities maintain >= 0.97 at N=200
- **MID:** one drops to 0.85-0.97 -> production claim weakened
- **HF:** any drops below 0.85 -> production claim fails Wilson lower bound

#### G5: AT-1 Entity substitution vs KF-1 (Adversarial Drill #1)
- **Anchor pointer:** adversarial_adaptive Section 4 Cell AT-1
- **Why now:** KF-1 paraphrase refuted only against OFF-SHELF MT (NLLB/MarianMT designed to preserve meaning); entity substitution with preserved bigrams is cheapest adaptive attack untested
- **Test:** generate test set with "Lyon" substituted for "Paris" while keeping all 8 surrounding bigrams identical (and analogous entity-class swaps); measure KF-1 AUC drop
- **Wall:** ~2 GPU-hours; CPU-feasible; SQuAD data available
- **HP:** KF-1 AUC drop <= 0.05 (entity sub doesn't break grounding)
- **MID:** 0.05-0.20 (degraded but usable)
- **HF:** > 0.20 (KF-1 requires NLI-based upgrade before deployment)

#### G6: AT-2 Semantically similar fabrication at middle hop (Adversarial Drill #2)
- **Anchor pointer:** adversarial_adaptive Section 4 Cell AT-2
- **Why now:** fact_checked_khop 1.000 HP may be artifact of random fabrication tests; semantically similar fabrications (cosine > 0.85 to true fact) NEVER tested
- **Test:** inject semantically similar fabrications (cosine_sim > 0.85 to true fact, different entity) at middle hop K/2; measure per-hop localization
- **Wall:** ~2 GPU-hours
- **HP:** localization accuracy >= 0.85 even at high cosine similarity
- **MID:** 0.65-0.85
- **HF:** < 0.65 -> per-hop verification needs hash-exact (not similarity-threshold) architecture

### TIER 3 -- Alternative encoder candidate

#### G7: E5-large-v2 geometry audit + capacity smoke (BGE Drill Cell 3)
- **Anchor pointer:** research_drill_BGE_d_eff_theory_failure_2x_2026-06-07.md Test 3
- **Why now:** E5-large-v2 uses weak supervised pre-training before strong fine-tuning -- predicted to preserve more isotropy than BGE-large
- **Test:** geometry audit first (PR + rho_eff); if passes 4-step protocol, run cap smoke at N=2048
- **Wall:** 5 min CPU geometry + 45 min GPU cap smoke if geometry passes; total ~50 min
- **HP:** PR > 120 AND rho < 0.20 AND cap > 200 -> third encoder candidate alongside Llama-1B + BGE+pinv
- **MID:** geometry passes but cap 80-200
- **HF:** geometry fails (PR < 40 or rho > 0.35)

### TIER 4 -- Deeper adaptive validation (lower priority)

#### G8: AT-3 Correlated KB anchoring bias test (Adversarial Drill #3)
- **Anchor pointer:** adversarial_adaptive Section 4 Cell AT-3
- **Why now:** anchoring-bias refutation GENUINE for independent synthetic; real KBs have semantic cluster structure
- **Test:** construct clustered KB (entity types grouped); inject false fact in cluster; measure propagation
- **Wall:** ~3 GPU-hours; requires clustered KB construction
- **HP:** no propagation under cluster structure
- **MID:** partial propagation only within tight clusters
- **HF:** significant propagation -> requires per-domain orthogonalization

#### G9: AT-5 Consistent-lie chain verification (Adversarial Drill #5)
- **Anchor pointer:** adversarial_adaptive Section 4 Cell AT-5
- **Why now:** multi-step fabrication chains where each hop is INDIVIDUALLY correct but chain conclusion is FALSE -- never tested
- **Test:** construct chains where each hop verifies but composition is wrong; measure chain-level catch rate
- **Wall:** ~2 GPU-hours + manual chain construction
- **HP:** chain-level catch >= 0.85 -> compositional verification works
- **HF:** < 0.65 -> end-to-end chain-composition verification is architectural gap (new capability needed)

---

## TOTAL BATCH G

- Tier 1 (G1-G3): ~75 min CPU/GPU; $0
- Tier 2 (G4-G6): ~7 GPU-hours; $0-15 cloud if needed
- Tier 3 (G7): ~50 min CPU/GPU; $0
- Tier 4 (G8-G9): ~5 GPU-hours; $0-12 cloud if needed
- **Total: ~13-15h compute; $0-30**

Mostly local CPU/GPU; cloud only if local GPU lane has capacity issues.

---

## F1/F2/F3 ORIGINAL ANCHORS LOCATED

You asked for original scripts; here they are:

### F1 norm-gate original
- **Script:** `experiments/exp_substrate_embedding_norm_gate_discriminability_v1.py`
- **Action:** re-run at M_max >= 300 + pinv where applicable; compare to original HF verdict

### F2 kf1_contradiction original
- **Script:** `experiments/exp_substrate_kf1_contradiction_detection_order_sensitive_v1.py`
- **Action:** re-run at M_max >= 300 + pinv; compare to original HF (negation detection)

### F3 kf1_truthfulqa original
- **Script:** `experiments/exp_substrate_kf1_truthfulqa_style_v1.py`
- **Action:** re-run at M_max >= 300 + pinv; compare to original HF (TruthfulQA-style)

All three are CPU; ~30 min each; $0 each.

---

## F9 PP-8 alpha=0.005 default swap GUIDANCE

I searched for PP-8 sparse-coding hardcoded alpha defaults and didn't find a single config file -- alpha is parameterized in experiment scripts (e.g., exp_sparse_alpha_fine_sweep_below_004_v1.py + hierarchical_hadamard cells).

**Your call on the right engineering scope:**
- Option A: update hdlab/ default if there's a single function that defaults to alpha; grep hdlab/ for `alpha=0.0` defaults
- Option B: standardize alpha=0.005 in all new PP-8 experimental scripts going forward (per discipline rule; no retroactive change)
- Option C: ship a config file `production_defaults.py` with `PP8_SPARSE_ALPHA = 0.005` that all production cells import

**Recommend Option B** (standardize in new scripts; no retroactive churn) plus document the cycle 142 finding as a comment in any cell that uses alpha for PP-8 work. Minimal blast radius; consistent with no-retroactive-edits discipline.

You know the production code paths best -- defer to your judgment on engineering scope.

---

## Dispatch sequence recommendation

**Immediate parallel (all Tier 1; ~75 min):**
- G1 geometric alignment audit (15 min CPU; LAPTOP OK)
- G2 pinv throughput benchmark (30 min CPU+GPU)
- G3 AT-4 fp16 overflow N=65536 (30 min CPU)

**Sequential after Tier 1 (Tier 2; ~7h GPU):**
- G4 AT-6 200-cell re-validation
- G5 AT-1 entity substitution vs KF-1
- G6 AT-2 semantically similar fabrication

**Parallel with Tier 2 if CPU lane open (Tier 3):**
- G7 E5-large-v2 geometry + cap smoke

**After Tier 2 verdicts:**
- G8 + G9 (AT-3 + AT-5) if Tier 2 reveals adversarial gaps

**F1/F2/F3 re-audits** can run in parallel with any Tier (CPU lane).

---

## SSOT updates

**Adopt corrected encoder selection protocol from BGE drill:**

```
Step 1: d_eff > 60 (existing)
Step 2: PR > 40 (NEW -- Participation Ratio)
Step 3: rho_eff < 0.35 (NEW -- mean pairwise cosine similarity)
Step 4: predicted_cap = alpha_c * N * (1-rho)^2 * (PR/d_ref) > 80
```

G1 measurement provides empirical PR + rho_eff for current encoders; future encoders pre-screened.

**Adopt corrected compound math from Batch F F7:**

The "stacking levers multiplicatively" framing from yesterday + cycle 142 was WRONG. Production picks BEST SINGLE LEVER per axis. pinv + sparse address the SAME bottleneck (correlation) and overlap. Multi-head is a DIFFERENT regime (support-recovery formalism; incompatible with dense-W).

**Realistic compound math (post Batch F F7):**
- pinv OR sparse (best single = sparse 24x; or pinv on real keys gives ~9x rescue)
- + CRT multi-scale (independent axis; potentially compounds)
- + sharding (independent axis; scales to arbitrary fact counts)
- + Llama-1B encoder choice (foundational lift)

This is much more modest than "millions to billions" but still substantial.

---

## Cross-references

- All 3 strategic drills (Drills A/B/C): notes/research_drill_*_2026-06-07.md
- Batch F partial status (F6 HP + F7 GENUINE HF + F8 HP): exp_dev_to_research_batchF_status_2026-06-07.md
- Cycle 142 retroactive audit: orchestrator_to_research_results_summary_2026-06-06_cycle142.md

---

## Contract

You design anchor specifics, sweep grids, HP/MID/HF thresholds (within frames provided), queue assignments, timeout formulas. Pre-reg per envelope-fail-band protocol. ASCII-only. Apply [[feedback-no-experiment-design-in-prompts]] -- this handoff names anchors + WHY + tier only.

F1/F2/F3 originals located above; re-run faithfully with M_max>=300 + pinv where applicable.

F9 engineering is your scope decision (Option B recommended; standardize in new scripts).

---

**END.**

**Exp-Dev:** Batch G authorized (9 cells; ~13-15h compute; $0-30). Tier 1 (G1-G3) is decisive at <2h. F1/F2/F3 originals located (paths in body). F9 your engineering scope (Option B recommended). Dispatch order recommendation in body; you override per queue state.

**User:** All authorized. 9 cells routed to Exp-Dev validating today's empirical claims at adaptive-adversary tier + grounding encoder theory + closing pinv throughput unknowns. Tier 1 (~75 min) gives decisive answers cheaply.

**Orchestrator + Testbed:** Visibility only.
