# exp_dev hand-off -- research: Gap E selective forgetting + importance-weighted compression (cortex-composed)

**Filed by:** research (Opus 4.7 1M)
**Filed at:** 2026-06-26
**Trigger:** USER deep drill on Gap E (selective forgetting + importance scoring); explicit cortex-composition emphasis. Companion research note: `notes/research_gap_E_selective_forgetting_importance_compression_2026-06-26.md`.

**Pause state:** Pause flag check is exp_dev's responsibility on pickup; this file is pickup-eligible whenever pause clears or for queue-refill on next emergency cycle.

**Per [[feedback-no-experiment-design-in-prompts]]:** This file POINTS to anchors and lit-evidence. Cell-author owns experiment design, hyperparameter selection, harness wiring, smoke tests, and pre-reg envelope-fail-band derivation.

**Cross-file relationship:** This hand-off EXTENDS the TWO_TIER + REM-cold-storage architectures with multi-factor importance scoring + cortex composition. All 3 anchors compose with the in-flight TWO_TIER cell (`exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md`) and require it to land HARD_PASS first. ANCHOR_1 here is the natural cortex-composed extension; ANCHOR_2 composes with the REM-revival ANCHOR_1 (recoverable cold storage); ANCHOR_3 composes with Gap 3 BCM (schema emergence).

---

## Anchor candidates (rank-ordered)

### ANCHOR_1 (rank-1, cheapest decisive, USER cortex-composition direct test)

- **Pointer:** `multi_factor_importance_cortex_composed_v1`
- **Substrate-product reading:** Extend the in-flight TWO_TIER cell's promotion path with a 6-signal importance vector: recency + query_freq + downstream_impact + surprise (4 substrate-mineable signals from existing telemetry) + schema_contribution (cosine vs W_schema centroids from Gap 3 BCM) + cortex_predicted_salience (W_pred @ atom_signature from n5 revival). The 6FACTOR-vs-4FACTOR ablation discriminates "more signals = noise reduction" from "cortex composition is load-bearing." 3 arms: TWO_TIER_SINGLE (rail), TWO_TIER_4FACTOR_NOCORTEX (substrate-mineable signals only), TWO_TIER_6FACTOR_CORTEX (full cortex composition). Brain-fidelity HIGH (mPFC + ATL + vmPFC + DA layer composition); cortex-composition USER-directed; substrate-better claim: 6 signals at full precision vs brain's ~3-4 at 1-bit dendritic integration, plus learnable weights vs evolutionary defaults.
- **Tier hint:** MEASURED_MECHANISM at first land; chain-grade-eligible if HARD_PASS_CORTEX_COMPOSED AND ablation gap (6FACTOR - 4FACTOR) >= 0.05 absolute AND signal independence audit passes (no two signals correlated > 0.85).
- **Why now:** Cortex layer is being spun up THIS WEEK. CRITICAL DISPATCH DEPENDENCY -- wait until TWO_TIER (in flight) lands HARD_PASS before dispatching this cell, because the W_old promotion path is the load-bearing scaffold. If TWO_TIER lands HARD_PASS_PARTIAL or MIDDLE_BAND, dispatch ANCHOR_1's 4FACTOR_NOCORTEX arm first (degrades gracefully without cortex composition).
- **P_deflated:** 0.50 (at novel-synthesis cap because cortex composition is novel synthesis of TWO_TIER + BCM + n5 primitives).
- **Cost:** ~3-5 CPU-hr local at N=4096, 3 arms, 3 seeds [11, 13, 19].
- **Reference for design context:** `notes/research_gap_E_selective_forgetting_importance_compression_2026-06-26.md` Section (b) + Section 5 Candidate 1.

### ANCHOR_2 (rank-2, recoverable cold-storage with multi-factor importance)

- **Pointer:** `recoverable_coldstorage_multi_factor_v1`
- **Substrate-product reading:** Extend REM-revival ANCHOR_1 (W_active + W_cold no-combine architecture) with the 6-signal importance vector from this drill's ANCHOR_1 + an explicit recovery path. On refuse-gate fire in W_active, scan W_cold; on cosine match above tau_cold_recovery, PROMOTE cold atom back to W_active. 4 arms: REM-ANCHOR_1 baseline (single-importance), this cell (6-importance + recovery), recovery-disabled ablation (6-importance no recovery), random-recovery ablation (recovery from random cold atom). This is the substrate-better claim made explicit -- brain pruning is irreversible, substrate's recovery is deterministic and bounded.
- **Tier hint:** MEASURED_MECHANISM at first land; chain-grade-eligible if HARD_PASS (recall_oldest in W_cold >= 0.70 AND recovery accuracy on held-out probe >= 0.80 AND W_active capacity post-recovery within 5%).
- **Why now:** ONLY-IF TWO_TIER HARD_PASS AND REM-revival ANCHOR_1 HARD_PASS first. Composes two unproven mechanisms; lower joint P; worth dispatching after individual validation.
- **P_deflated:** 0.45.
- **Cost:** ~5-7 CPU-hr local at N=4096, 4 arms, 3 seeds.
- **Reference for design context:** `notes/research_gap_E_selective_forgetting_importance_compression_2026-06-26.md` Section 5 Candidate 2.

### ANCHOR_3 (rank-3, schema-emergence-based forgetting)

- **Pointer:** `schema_emergence_protect_importance_v1`
- **Substrate-product reading:** Use Gap 3 BCM's W_schema centroids to identify atoms that contribute to emerging schemas; protect those atoms from migration (immortality gate on TWO_TIER's promotion path); compress atoms with low schema-contribution into schema centroids over time. 4 arms: TWO_TIER baseline (no schema signal), TWO_TIER + schema_contribution as 5th signal (additive lift test), TWO_TIER + binary schema_protect gate (atoms above tau are immortal in W_active), schema_emergence_decay (atoms below tau lose protection over time). Brain-fidelity VERY HIGH (cortex schema-formation pathway mPFC-MTL vs mPFC-HPC, 2025 review).
- **Tier hint:** MEASURED_MECHANISM at first land; chain-grade-eligible if HARD_PASS AND schema-protected atom count stays within [5%, 15%] of total (sanity check) AND schema-protected atoms have recall accuracy >= 0.95 at J=10000.
- **Why now:** ONLY-IF Gap 3 BCM HARD_PASS first. Cell depends on W_schema centroids being meaningful; if BCM is in flight or HARD_FAIL the schema signal is noise.
- **P_deflated:** 0.40.
- **Cost:** ~4-6 CPU-hr local at N=4096, 4 arms, 3 seeds.
- **Reference for design context:** `notes/research_gap_E_selective_forgetting_importance_compression_2026-06-26.md` Section 5 Candidate 3.

### ANCHOR_4 (rank-4, LSM-tree cross-domain diagnostic ablation)

- **Pointer:** `lsm_tree_compaction_importance_v1`
- **Substrate-product reading:** RocksDB / HotRAP style: 4 importance signals (Least Overlapping, Coldest, Oldest, Tombstone Density mapped to substrate analogs) as a baseline policy. Pure engineering analog with NO cortex composition; diagnostic to bound how much of ANCHOR_1's lift comes from cortex composition vs simpler DB-style policies. 2 arms: TWO_TIER + LSM-style 4-signal importance; TWO_TIER + ANCHOR_1's 6-signal importance (already-dispatched). Direct comparison.
- **Tier hint:** MEASURED_MECHANISM diagnostic; useful for cap_map even if HARD_FAIL.
- **Why now:** ONLY-IF ANCHOR_1 lands MIDDLE_BAND -- helps localize whether cortex composition is the load-bearing addition or whether simpler engineering policies recover most of the lift.
- **P_deflated:** 0.35.
- **Cost:** ~2-3 CPU-hr local at N=4096, 2 arms, 3 seeds.
- **Reference for design context:** `notes/research_gap_E_selective_forgetting_importance_compression_2026-06-26.md` Section 4 M4.

---

## Context pointers (file paths only, not summaries)

- Primary research note (this drill): `notes/research_gap_E_selective_forgetting_importance_compression_2026-06-26.md`
- Parent TWO_TIER (in flight, load-bearing dispatch dependency): `notes/exp_dev_gap4_two_tier_generational_W_v1_DISPATCHED_2026-06-26.md`
- Sibling REM revival (ANCHOR_1 dispatch-eligible): `notes/exp_dev_handoff_research_REM_revival_cold_storage_never_delete_2026-06-26.md`
- Sibling brain selective homeostasis: `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md`
- Sibling cortex-as-router (mPFC analog source): `notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md`
- Sibling slow_cortex_bigram (W_pred source): `notes/research_n5_revival_slow_learning_cortex_context_2026-06-26.md`
- Sibling Gap 3 BCM schema-emergence (W_schema source): `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md`
- Parent gap 4 continual learning: `notes/research_gap4_continual_5x_drill_2026-06-26.md`
- Brain CLS drill: `notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md`

---

## Contract

This hand-off file does NOT design experiments. Cell-author owns:
- Experiment design (signal weight w_k tuning; tau thresholds for schema_protect; recovery promotion bonus; K_promote / J_migrate cadences)
- Pre-reg envelope-fail-band derivation (per [[feedback-envelope-fail-bands]])
- Smoke test (per [[feedback-cell-author-smoke]]) -- IMPORTANT: smoke MUST verify (a) signal independence (no two signals correlate > 0.85 on a held-out batch), (b) importance vector distribution is non-degenerate (not all atoms at near-uniform importance), (c) cortex signal availability (W_schema + W_pred matrices loadable from disk or in-memory from current run) BEFORE launching full ingest.
- Harness wiring (sequence-eval bands per substrate cert architecture C0-C6; multi-task discriminator with task-A/B/C labeled by ingest cycle; per-arm metrics MANDATORY per Fix #28)
- Post-ship REMOTE VERIFY (per [[feedback-post-ship-verify]])
- Self-test (per [[feedback-formula-selftests]])
- GPU dispatch route via hdi_orchestrator if N_DIM >= 8192 OR M >= 100k (per Fix #24)
- Pre-dispatch verify-the-referent (per Fix #26): check that TWO_TIER landed HARD_PASS in recent_landings.jsonl BEFORE dispatching ANCHOR_1; check that Gap 3 BCM landed HARD_PASS before ANCHOR_3; check that REM-revival ANCHOR_1 landed HARD_PASS before this ANCHOR_2.

Compute estimates are research's best guess; cell-author re-derives from harness reality.

---

## Autonomy declaration

This hand-off file is structural feed from research to exp_dev. exp_dev auto-discovers it on emergency-refill cycles (scan `notes/exp_dev_handoff_*.md` sorted by mtime). Research filing this file does NOT obligate exp_dev to ship in any specific order; exp_dev applies its own pause-flag check, queue-state inspection, GPU-routing rule (Fix #24), and pre-dispatch verify-the-referent gate (Fix #26) before picking up any anchor.

**Dispatch ordering recommendation:**

1. **First** (when in-flight TWO_TIER lands HARD_PASS): ANCHOR_1 `multi_factor_importance_cortex_composed_v1` -- cheapest decisive cortex-composed test; degrades gracefully via 4FACTOR_NOCORTEX arm if cortex layer not yet mature.
2. **Conditional on ANCHOR_1 HARD_PASS_CORTEX_COMPOSED AND Gap 3 BCM HARD_PASS:** ANCHOR_3 `schema_emergence_protect_importance_v1` -- adds schema-immortality gate.
3. **Conditional on ANCHOR_1 HARD_PASS AND REM-revival ANCHOR_1 HARD_PASS:** ANCHOR_2 `recoverable_coldstorage_multi_factor_v1` -- full three-tier with recovery path.
4. **Conditional on ANCHOR_1 MIDDLE_BAND only:** ANCHOR_4 `lsm_tree_compaction_importance_v1` -- diagnostic ablation.

**DO NOT dispatch any of the 4 before TWO_TIER lands.** The in-flight cell is the load-bearing scaffold. All 4 anchors extend TWO_TIER -- they are not alternatives to it.

**The cortex-composition framing is mathematically sound and brain-grounded** (5 independent lit-precedents this drill, plus 3 from sibling drills: mPFC selective relevance signaling 2024, mPFC-MTL / mPFC-HPC schema pathways 2025 review, Heavy Hitters / SnapKV / Expected Attention LLM analogs, HotRAP / RocksDB DB analogs, HSG-ACKR HD-graph pruning). This is exp_dev-actionable IMMEDIATELY when TWO_TIER lands HARD_PASS; ANCHOR_1 is the cheapest decisive single cell to start.

-- research (Opus 4.7 1M)
