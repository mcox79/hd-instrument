# exp_dev hand-off — research: K_max NESS correction drill

**Filed-by:** research:opus, 2026-06-20
**Trigger:** USER directive 2026-06-20 implementing recommendation B from negatives discussion; drill-until-solutions on K_max-pessimistic open negative.
**Research note:** `notes/research_K_max_NESS_correction_drill_2026-06-20.md` (full citations + HARD-PASS/HARD-FAIL bands there)

**Pause state:** Per [[feedback-no-experiment-design-in-prompts]], this hand-off is anchor pointers + substrate-product reading + tier hints. exp_dev owns experiment design; this file does NOT prescribe cell-build details. Honor `data/orchestrator_paused.flag` before any dispatch.

---

## Why-now

Equilibrium Hopfield formula `K_max ≈ 3.3 × (1 − α/α_c)² / α` is PESSIMISTIC by 2-6× at substrate operating point. Empirical anchors (SQ2 K=12 single-substrate HP, hierarchical 24-hop HP, cleanup-augmented 6× depth boost) sit in a literature gap — no published closed-form for NESS-corrected K_max(α, write_rate, decay_rate). The substrate-product story is the empirical envelope; this hand-off opens the envelope-sweep cell that ships that envelope as a load-bearing claim.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (PRIMARY — CPU, cheap, ships envelope) — Tier 1 empirical depth-bound envelope sweep

- **Anchor pointer:** new cell `hdlab/experiments/K_max_NESS_envelope_sweep.py` (paths suggestive; exp_dev names)
- **Substrate-product reading:** validates the substrate-product depth-bound claim. Output is a parametric envelope K_max_observed(α, write_rate, decay_rate) that ships as "substrate operates 2-6× above equilibrium K_max formula in regime X." This is the load-bearing capability for the K_max-pessimistic open-negative scorecard row.
- **Tier hint:** Tier-1 (CPU pre-flight); ~2 hr CPU; if envelope confirmed, queue Tier-3 GPU validation.
- **Pre-reg bands (from research note section c, P1+P3):**
  - HARD-PASS: K_max_observed / equilibrium_formula ≥ 2.0 across ≥4 of 5 (write, decay) sweep points AND partial-correlation slope of K_max vs log(write_rate / decay_rate) > 0.5
  - HARD-FAIL: ratio < 1.3 across ≥3 of 5 points OR write & decay show independent (not ratio-only) dependence
  - MIDDLE-BAND: ratio in [1.3, 2.0]; ships as "1.5× envelope" instead of "2-6× envelope"
- **Why now:** USER directly authorized this drill 2026-06-20; the empirical anchors already exist; this sweep ratifies the envelope shape so the depth-bound is productizable rather than method-config-contingent.

### Anchor 2 (SECONDARY — CPU, cleanup-resharpening validation) — cleanup-on / cleanup-off depth-multiplier sweep

- **Anchor pointer:** extend or branch from the existing cleanup-augmented depth experiment (the one that produced the 6× empirical 2026-06-05).
- **Substrate-product reading:** ratifies P2 (cleanup-boost ≥ 5×) across the (write_rate, decay_rate) sweep grid from Anchor 1. Output: confirms cleanup-augmentation is the load-bearing depth-extension primitive (not a single-operating-point fluke).
- **Tier hint:** Tier-2 (CPU; can be folded into Anchor 1 sweep as an additional cell-axis).
- **Pre-reg bands:**
  - HARD-PASS: cleanup-on / cleanup-off K_max ratio ≥ 5.0 across ≥4 of 5 sweep points
  - HARD-FAIL: ratio < 2.0 across ≥3 of 5 points (cleanup-boost is regime-narrow)
- **Why now:** the 6× empirical is currently a single-operating-point anchor; this generalizes it to an envelope claim.

### Anchor 3 (TERTIARY — GPU, production-scale validation) — Tier 3 NESS-Hopfield K_max validation cell

- **Anchor pointer:** GPU validation cell at substrate's production operating point α ≈ 0.03; sweep N ∈ [256, 1024, 4096] × 10 seeds × 3 noise levels.
- **Substrate-product reading:** statistical backing (~30 data points) for the substrate's actual production depth-bound. Output: the substrate-product depth-bound claim is no longer "1 anchor" but "30-data-point envelope at production scale."
- **Tier hint:** Tier-3 (GPU; ~4 hr; ship only AFTER Anchor 1 envelope is confirmed).
- **Pre-reg bands:** match Anchor 1; this is the production-scale ratification.
- **Why now:** opportunistic — if Anchor 1 succeeds, the GPU validation closes the productization story.

### Anchor 4 (FUTURE — theory work; not exp_dev-shippable) — algebraic re-derivation

NOT an exp_dev anchor; flagged here for visibility. The Tier 2 theory work — couple Kalaj-Λ recursion (arXiv:2510.19146) with Betteti escape-time (arXiv:2603.03201) — is a Skunkworks/research multi-week theory item. If anchored later, this generates a substrate-novel closed-form K_max(α, write, decay) for productization beyond the empirical envelope. P_deflated 0.40 the synthesis is tractable in-house.

---

## Context pointers (file paths; no summaries)

- Research note (mandatory read): `d:/AI/hd-instrument/notes/research_K_max_NESS_correction_drill_2026-06-20.md`
- Empirical anchors:
  - SQ2 K=12 single-substrate HP (2026-06-05 cap_map row)
  - Hierarchical 24-hop HP (2026-06-05 cap_map row)
  - Cleanup-augmented 6× depth boost (2026-06-05 01:20 scorecard entry; "future-drill candidate" flag)
- Prior related drills:
  - `d:/AI/hd-instrument/notes/research_negative_N6_resonator_dense_V100_HF_2x_2026-06-20.md` (closes resonator framing as not informing K_max)
  - `d:/AI/hd-instrument/notes/research_modern_hopfield_PCN_AM_universal_kernel_2x_2026-06-17.md` (modern Hopfield is one-shot; not depth-extension)
- Substrate framework files (for envelope-sweep cell design): `d:/AI/hd-instrument/hdlab/` family per CLAUDE.md verification discipline (oracle in `verification/theory.py`; cell ships green pytest first per CLAUDE.md)

---

## Contract section

1. **exp_dev owns experiment design** — this file provides anchor pointers + substrate-product readings + tier hints + pre-reg bands. exp_dev decides cell structure, dispatch, and (write_rate, decay_rate, α) sweep grid.
2. **Pre-reg HARD-PASS / HARD-FAIL / MIDDLE-BAND bands are sacrosanct both directions** per [[feedback-negativity-bias]] — pre-reg before dispatch; honor both directions.
3. **CHECKPOINT-RESUME** per [[feedback-long-cells-must-checkpoint-resume]] — long sweep cells must demonstrate kill-restart resume.
4. **VERSION-MARKER discipline** — metrics must match the EXPECTED run version, not "file exists."
5. **Substrate verification discipline** per CLAUDE.md — every framework feature ships with a scaffold-free witness in `verification/`; pytest verification/ must be green.
6. **No LLM-in-the-loop** for envelope cells — pure substrate.

---

## Autonomy declaration

This file is auto-discovered by exp_dev on emergency-refill cycles (scan `notes/exp_dev_handoff_*.md` sorted by mtime). exp_dev is autonomous on pickup ordering, cell design, dispatch venue (CPU vs GPU), and statistical packaging. Research is on-call for follow-up Tier 2 theory work if the envelope sweep PASSES and motivates closed-form derivation.

**Honor pause flag** `data/orchestrator_paused.flag` — no dispatch if present.
