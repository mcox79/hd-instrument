# exp_dev hand-off: bounded-iteration recurrent-cleanup head probe (multi-hop scoped)

**Filed:** 2026-05-25 by Research sub-agent.
**Status:** READY for exp_dev pickup. Narrow scoped probe, NOT a primitive rebuild.
**Parent note:** `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md`
**Trigger:** strategic primitive decision LOCKED at LINEAR-HETEROASSOC primary; ONE narrow recurrent variant probe scoped to multi-hop K6 / d-cliff regime is the only design-space addition.

---

## TASK

Falsify (or queue further work on) the hypothesis that a **bounded-iteration sign-Hopfield cleanup head** on top of the existing linear-heteroassoc W primitive improves multi-hop d-cliff retrieval. The probe is **scoped narrowly** to multi-hop tests; this is NOT a substrate-wide rebuild.

The probe compares two readout heads applied to the SAME W = (1/N) Σ v_i k_i^T storage:

- **Arm A (linear baseline):** y = W k; report cosine. This is the existing substrate behavior.
- **Arm B (bounded recurrent cleanup):** y_0 = W k; y_{t+1} = sign((1/N) Σ_j ⟨y_t, v_j⟩ k_j); report y_T cosine at small T.

Storage is unchanged; only the readout differs.

---

## WHY

The primitive-decision note (parent) concluded that the LINEAR primitive wins decisively for MoE, retention rehab, CPU-edge, audit reproducibility, and discrete-plateau preservation. **The one capability where the lit-signal supports a possible recurrent benefit is multi-hop / hierarchical compositional binding** (Pollack RAAM lineage; iterative resonator decomposition; modern-Hopfield deep-Boltzmann generalizations).

The substrate's existing ACF resonator rescue is **already** a bounded-iteration refinement on top of linear storage and recovers atoms past K/N=1.5 — proof that the hybrid linear+iterative pattern works at the decomposition layer. The question for multi-hop is whether the analogous pattern works for the d=25 cliff.

**The probe MUST falsify or constrain** — diffuse "maybe helps" outcomes do not warrant a multi-hop-mode config knob. Either we get a HARD-PASS signal that warrants the knob, a HARD-FAIL that closes the recurrent variant for multi-hop, or a characterized MIDDLE band documenting the conditional benefit.

---

## CONTRACT

### Pre-registered HARD-PASS

Recurrent arm B improvement ≥ +0.10 per-hop retrieval accuracy at d=25, in ≥ 3 of 4 M-grid cells, with CI width < 0.05 across seeds.

→ Queue the multi-hop-mode config knob design (separate handoff). Document the recurrent-variant capability against the cap_map under a NEW row "multi-hop bounded recurrent cleanup". Update primitive-decision note status.

### Pre-registered HARD-FAIL

Recurrent arm B ≤ linear arm A at d=25 in ≥ 3 of 4 M-grid cells (any non-positive delta).

→ Close the recurrent-variant question for multi-hop. The primitive decision tightens to "linear is sole primitive across all evaluated tasks". File closure annotation in primitive-decision note.

### Pre-registered MIDDLE BAND

Recurrent arm B delivers +0.03 to +0.10 in 1–2 cells, sub-threshold in other cells.

→ Document the conditional benefit (which M/K cells benefit) WITHOUT queueing a full mode knob. Revisit only if Bet N rehab path closes via other axes. Annotate primitive-decision note with the conditional-benefit profile.

### Pre-registered INSTRUMENTATION-FAIL

Arm B fails to converge (oscillation; sign-Hopfield divergence) at T ≤ small bounded iteration count in > 20% of cells; OR CI width ≥ 0.10 (excessive seed variance).

→ Investigate convergence behavior before any verdict. Sign-Hopfield non-convergence at small T is itself diagnostic about the substrate's basin structure.

### Self-test cells (per [[feedback-strategy-spec-formula-selftests]])

The cleanup-head recurrence formula `y_{t+1} = sign((1/N) Σ_j ⟨y_t, v_j⟩ k_j)` is itself a verifiable form:

1. At t=0 with y_0 = W k_query, if k_query equals a stored k_i exactly, expected ⟨y_0, v_i⟩ ≈ 1 (within crosstalk noise) → y_1 ≈ sign(v_i) → if v_i is bipolar, y_1 = v_i exactly. **Pair: stored exact-match → y_1 recovers v_i.**
2. At t=0 with y_0 = random bipolar vector independent of all stored items, expected ⟨y_0, v_j⟩ ≈ 0 for all j → y_1 has near-zero expected magnitude → undefined sign → diagnostic for the random-init basin behavior. **Pair: random init → y_1 has E[|inner|] ≈ √(M/N).**
3. The recurrence at T=1 with y_0 = W k_query is structurally a **second pass through the same outer-product storage** — i.e., approximating a one-step iterative pseudoinverse correction. **Pair: T=1 should match the published "iterated linear cleanup" performance lift, ~5–10% at high-α.**

exp_dev MUST verify these self-tests on the implementation BEFORE shipping the probe.

---

## AUTONOMY

exp_dev decides:
- Anchor names
- Specific M-grid points (4 values bracketing the expected useful range; suggest order-of-magnitude span)
- Specific d values (3 values bracketing d=25 cliff)
- K values (≥ 1 K value; K=8 is the existing multi-hop reference)
- Bounded-iteration count T (small; suggest T ∈ {2, 3, 5} as candidates)
- Seeds (≥ 5 for CI)
- Queue placement (CPU vs GPU vs local-CPU)
- ETA
- N (the substrate-default N=4096 is the obvious choice but exp_dev may sub-sample for cost)
- Pre-reg artifact name + path
- Verdict-emission format

This handoff specifies the TASK (what to test), the WHY (mechanistic motivation), and the CONTRACT (pass/fail/middle band thresholds + self-tests). It does NOT specify the engineering choices above.

---

## Cross-references

- Parent decision note: `notes/research_primitive_decision_linear_vs_recurrent_2026-05-25.md`
- Existing multi-hop tooling: cap_map v60 (Bet N KILLED), v77 (Bet X unifying d=25 = compositional-depth bound), `acf_K_dependent_retry` (existing ACF resonator rescue at decomposition layer)
- Existing linear-heteroassoc baseline: `experiments/exp_wave14_moe_alpha_c_prestep_v1.py` (the W storage form is the same here)
- Mesoscopic-transport lens on multi-hop: `notes/research_mesoscopic_transport_moe_2026-05-25.md` (informs which cells should benefit if HARD-PASS)

---

**End hand-off.**

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
