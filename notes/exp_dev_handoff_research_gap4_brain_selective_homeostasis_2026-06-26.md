# exp_dev hand-off — research: GAP 4 brain SELECTIVE homeostasis (level-2 drill)

**Filed by:** research (Opus 4.7)
**Filed at:** 2026-06-26
**Trigger:** Level-2 operational drill on Cell B (REM homeostasis) HARD_FAIL_DESTROYS_OLDER (3 schedules); companion research note `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md`.

**Pause state:** Pause flag check is exp_dev's responsibility on pickup; this file is pickup-eligible whenever pause clears or for queue-refill on next emergency cycle.

**Per [[feedback-no-experiment-design-in-prompts]]:** This file POINTS to anchors and lit-evidence. Cell-author owns experiment design, hyperparameter selection, harness wiring, smoke tests, and pre-reg envelope-fail-band derivation.

**Cross-file relationship:** This hand-off extends `notes/exp_dev_handoff_research_gap4_continual_5x_2026-06-26.md` (TWO_TIER hand-off currently in flight). The anchors below COMPOSE with TWO_TIER (M5 STC tagging provides the PROMOTION CRITERION for TWO_TIER promotion). If TWO_TIER lands HARD-PASS, dispatch ANCHOR_2 (STC) as the natural follow-on. If TWO_TIER lands HARD-FAIL, dispatch ANCHOR_1 (magnitude-gated, cheapest decisive) as a diagnostic of whether selectivity (not architecture) is the issue.

---

## Anchor candidates (rank-ordered)

### ANCHOR_1 (rank-1, cheapest decisive)

- **Pointer:** `gap4_magnitude_gated_downscale_v1`
- **Substrate-product reading:** Replace Cell B's `W *= 0.99` (global) with `W[|W| > w_thresh] *= gamma_high; W[|W| <= w_thresh] *= 1.0` — single masked multiply that preserves small weights (old/dwindling patterns near cleanup threshold) and only downscales loud-and-recent weights. Brain-fidelity LOW but diagnostic: directly tests whether Cell B's failure was "downscale itself" or "downscale touching small weights." If PASS, the mechanism family is fine, just needs the threshold. If FAIL, downscale itself is wrong-family and pivot to ANCHOR_2 STC.
- **Tier hint:** MEASURED_MECHANISM at first land; chain-grade-eligible only if produces durable forgetting-curve flattening across multiple alpha regimes.
- **Why now:** ONE CPU-hour smoke; directly diagnoses Cell B's HARD_FAIL root cause; lowest substrate-distance (~5-line change to existing Cell B code). No new primitives needed.
- **P_deflated:** 0.45.
- **Reference for design context:** `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md` Section 3 M1 + Section 5 Cell 1.

### ANCHOR_2 (rank-2, highest brain-fidelity, most substrate-novel)

- **Pointer:** `gap4_stc_capture_selective_downscale_v1`
- **Substrate-product reading:** Implement Synaptic Tagging and Capture (Frey-Morris 1997) — three matrices alongside W: T[i,j] (tag, decays after K cycles), P[i,j] (persistent, immune to future downscale). Tag fires when `|dW[i,j]| > theta_tag` at write time. Every J_replay cycles, sample N_PRP tagged weights (top-Ca or uniform) → mark persistent. Global downscale (now safe) skips persistent: `W[~P] *= gamma; W[P] *= 1.0`. Bounded-PRP-pool is the KEY mechanism — enforces COMPETITION under scarce protein resources, exactly what makes brain selectivity scarce-resource-bounded rather than threshold-bounded. ZERO substrate prior on STC.
- **Tier hint:** MEASURED_MECHANISM if HARD-PASS alone; chain-grade-eligible if HARD-PASS composes with TWO_TIER (provides promotion criterion).
- **Why now:** Most brain-aligned mechanism + most novel for substrate + composes architecturally with in-flight TWO_TIER cell. If this passes, substrate has the full per-weight selectivity vocabulary the brain uses.
- **P_deflated:** 0.45.
- **Reference for design context:** `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md` Section 3 M5 + Section 5 Cell 2.

### ANCHOR_3 (rank-3, composes for indefinite continual operation)

- **Pointer:** `gap4_composed_NREM_plus_selective_REM_v1`
- **Substrate-product reading:** Compose Cell A (NREM replay, currently MIDDLE_BAND drift_red=0.067) with ANCHOR_2 STC: every 100 cycles do NREM replay; every 500 cycles do STC selective downscale. The two hit DIFFERENT failure modes — replay strengthens the dwindling tail; selective downscale prevents capacity saturation by retiring un-reaccessed patterns. The load-bearing test for "substrate can ingest indefinitely without bounded-capacity collapse."
- **Tier hint:** chain-grade-eligible IF HARD-PASS at J=10000 cycles AND ||W||_F stays bounded AND effective_dimensions_used stays <= 80% of N. This is the existence proof for the L2 glass-box-LLM moat.
- **Why now:** ONLY-IF ANCHOR_2 HARD-PASS individually. Long-horizon cell (~6-8 CPU-hr) — only worth dispatching when M5 individually passes.
- **P_deflated:** 0.30 (composition risk; ordering interactions).
- **Reference for design context:** `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md` Section 4 + Section 5 Cell 3.

### ANCHOR_4 (rank-4, theoretical EWC anchor)

- **Pointer:** `gap4_ewc_fisher_importance_gated_v1`
- **Substrate-product reading:** Fisher-diagonal importance gate: F[i,j] = EWMA(|W[i,j]|² × access_count[i,j]); downscale = `W[F < f_thresh] *= gamma; rest *= 1.0`. Uses the Logits-Reversal correction from arxiv 2603.18596 (March 2026) to avoid the vanishing-gradient bug in naive EWC. This is the literal EWC formalism, which is itself the abstracted version of STC-bounded-protein-competition.
- **Tier hint:** MEASURED_MECHANISM expected; theoretical anchor for "Bayesian regularization view of per-weight selectivity."
- **Why now:** ONLY-IF both ANCHOR_1 AND ANCHOR_2 land MIDDLE_BAND or HARD-FAIL. Provides a theoretical fallback with explicit Fisher-info justification.
- **P_deflated:** 0.40.
- **Reference for design context:** `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md` Section 3 M3.

### ANCHOR_5 (rank-5, recency-based timestamp ledger)

- **Pointer:** `gap4_recency_gated_downscale_v1`
- **Substrate-product reading:** Track per-weight last-touched timestamp T[i,j]; downscale only weights touched within last K cycles. Old/untouched weights preserved exactly. Substrate analog of "tag decays in 1-3 hours" (STC) but with purely temporal selectivity (no Ca-magnitude gate).
- **Tier hint:** MEASURED_MECHANISM if HARD-PASS.
- **Why now:** Backup if ANCHOR_1 PASS is borderline (MIDDLE_BAND); adds temporal selectivity orthogonally. Cost ~2 CPU-hr; per-weight timestamp tolerable (~10MB at N=2048 bf16).
- **P_deflated:** 0.45.
- **Reference for design context:** `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md` Section 3 M2.

---

## Context pointers (file paths only, not summaries)

- Primary research note (this drill): `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md`
- Parent 5x drill: `notes/research_gap4_continual_5x_drill_2026-06-26.md`
- Sibling TWO_TIER hand-off (in flight): `notes/exp_dev_handoff_research_gap4_continual_5x_2026-06-26.md`
- Brain CLS drill: `notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md`
- Cell A NREM replay (MIDDLE_BAND ledger entry): substrate cert_ledger.jsonl
- Cell B REM homeostasis HARD_FAIL_DESTROYS_OLDER (3 schedules): substrate cert_ledger.jsonl

---

## Contract

This hand-off file does NOT design experiments. Cell-author owns:
- Experiment design (hyperparameters, schedule, arms)
- Pre-reg envelope-fail-band derivation (per [[feedback-envelope-fail-bands]])
- Smoke test (per [[feedback-cell-author-smoke]])
- Harness wiring (META_M7 LM-eval where applicable; sequence-eval bands per substrate cert architecture C0-C6)
- Post-ship REMOTE VERIFY (per [[feedback-post-ship-verify]])
- Self-test (per [[feedback-formula-selftests]])

Compute estimates are research's best guess; cell-author re-derives from harness reality.

---

## Autonomy declaration

This hand-off file is structural feed from research to exp_dev. exp_dev auto-discovers it on emergency-refill cycles (scan `notes/exp_dev_handoff_*.md` sorted by mtime). Research filing this file does NOT obligate exp_dev to ship in any specific order; exp_dev applies its own pause-flag check, queue-state inspection, GPU-routing rule (Fix #24), and pre-dispatch verify-the-referent gate (Fix #26) before picking up any anchor.

Compose-with-TWO_TIER ordering note: if `gap4_two_tier_generational_W_v1` (currently in flight) HARD-PASSes, exp_dev should prefer ANCHOR_2 STC (provides the natural promotion criterion). If it HARD-FAILs, exp_dev should prefer ANCHOR_1 magnitude-gated (cheapest decisive diagnostic of whether selectivity itself is the missing ingredient or whether the architecture also needs fixing).
