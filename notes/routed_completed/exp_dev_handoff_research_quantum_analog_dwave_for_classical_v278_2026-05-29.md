# exp_dev hand-off — research: substrate-as-classical-AQC quantum-inspired probes (v278)

**Filed by:** research sub-agent (Opus deep-drill)
**Trigger:** `notes/research_quantum_analog_dwave_for_classical_v278_2026-05-29.md` — DEEPER drill on classical-AQC positioning + quantum-inspired classical experiments
**Filed:** 2026-05-29

**Pause state:** check `data/orchestrator_paused.flag` at pickup time (research filing is NOT pause-gated; exp_dev dispatch IS).

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: anchor name, N, M, seed count, threshold formula bounds, smoke profile, FULL profile, queue choice, ETA, timeout value.

---

## Why this hand-off (research finding summary)

User reframing 2026-05-29: substrate is structurally a classical analog of adiabatic quantum computation (D-Wave's problem class), specifically the maximally-stoquastic / commutative / Bravyi-Terhal classically-simulable limit. This drill confirmed the framing is mathematically defensible AND opened two concrete quantum-inspired experiments that test whether the substrate captures unrealized AQC-style benefits.

Two actionable experiments (one cheap, one moderate-cost) with pre-registered HARD-PASS / HARD-FAIL bands. Neither is a positioning blocker (the secondary classical-AQC narrative is defensible independent of these experiments) but BOTH would add product features to the killer-features roster if HARD_PASS.

## Anchor candidates (rank-ordered)

### Anchor 1 (top recommendation) — QE-1 SUBSTRATE BETA-ANNEALING DURING RETRIEVAL

- **Anchor pointer (concept):** introduce a beta-annealing schedule on substrate retrieval (instead of zero-T greedy argmax); measure whether annealed retrieval reaches lower-energy basins or higher accuracy at high-noise queries
- **Reading of substrate-product implication:** if HP -> productizable "robust retrieval mode" feature complementing KF-1 hallucination detection; classical-AQC positioning empirically validated. If HF -> classical-AQC framing remains theoretical-only (still defensible for buyer-channel) but no annealing-mode product feature
- **Tier hint:** GPU smoke at N=2048 3-seed; ~1 GPU-day for smoke + 1 GPU-day for FULL if smoke HP; promote to FULL at N=8192 5-seed only if smoke HP
- **Why now:** cheapest probe across the two QE candidates; directly tests whether substrate has unexploited basin-structure capacity under temperature-gradient dynamics; classical-AQC positioning empirical anchor
- **Research-note pointer:** `notes/research_quantum_analog_dwave_for_classical_v278_2026-05-29.md` Section D / QE-1 — HARD-PASS / HARD-FAIL bands pre-registered (HP1 >= 5% lower retrieval energy at any sigma, HP2 retrieval accuracy >= greedy at sigma=0.40; HF1 strictly worse across all beta schedules)
- **Cap_map row pointer:** would open a NEW row "beta-annealed retrieval mode" (currently no annealing-mode row in cap_map); ties to D1 Glauber dynamics field-advisor candidate

### Anchor 2 — QE-3 SYNDROME-BASED ERROR CORRECTION ON KERDOCK SUBSTRATE

- **Anchor pointer (concept):** active syndrome decoding at substrate readout time using Kerdock(16) parity-check matrix; correct retrieval errors that escape basin attraction
- **Reading of substrate-product implication:** if HP -> productizable "error-corrected retrieval" feature on N=65536 Kerdock substrate; positions against ANY content-addressable memory architecture (substrate + active correction). If HF -> standard basin retrieval already captures parity-check capacity (no benefit)
- **Tier hint:** ~3-5 days engineering for Kerdock parity-check decoder implementation + ~1 GPU-day smoke at N=8192 (Kerdock(13)) + ~1 GPU-day at N=65536 (Kerdock(16)); CPU evaluation may be feasible since decode is per-query
- **Why now:** complementary to QE-1 (different rescue mechanism: QE-1 is basin-structure-aware, QE-3 is coding-theory-aware); both are quantum-inspired classical techniques; KF-1 Kerdock anchor production-scale N=4096 5-seed already HARD_PASS v271 (foundation present)
- **Research-note pointer:** `notes/research_quantum_analog_dwave_for_classical_v278_2026-05-29.md` Section D / QE-3 — HP1 >= 10% accuracy improvement at sigma=0.40; HF1 <= 2% improvement (within seed noise); HF2 syndrome decode latency >> retrieval latency (kills productization)
- **Cap_map row pointer:** would extend N=65536 codebook row (currently 0.42-0.55 P per v89) with active correction; ties to coding-theory field tier-2 anchor

### Anchor 3 (stretch) — TANG-STYLE AMPLITUDE-ESTIMATION CONFIDENCE INTERVALS

- **Anchor pointer (concept):** apply Tang 2019 L2-norm sampling framework to substrate retrieval to produce confidence-interval-style readout ("atom_i retrieved with probability 0.92 +/- 0.03")
- **Reading of substrate-product implication:** enriches KF-1 hallucination detection API with confidence bands; could increase pricing power on existing KF-1 lane
- **Tier hint:** ~1-2 weeks engineering for L2-sampling-based retrieval-probability estimator; CPU evaluation likely
- **Why now:** quantum-inspired classical technique directly portable to substrate; KF-1 is already production-ready (v271 N=4096 5-seed HARD_PASS) and would benefit from confidence-interval extension
- **Research-note pointer:** `notes/research_quantum_analog_dwave_for_classical_v278_2026-05-29.md` Section C item (b)
- **Cap_map row pointer:** extends KF-1 hallucination-detection row with confidence-band capability

### Anchor 4 (NOT IN SCOPE) — QE-2 coherent multi-hop retrieval

This anchor is owned by the parallel agent drill per the dispatch note. The substrate equivalent (pre-argmax retrieval distribution maintained through intermediate hops) is ALREADY in pipeline as `kf45_pre_argmax_joint_probe_v1_n4096` per status log. NO separate hand-off needed. Cross-referenced for completeness.

## Recommended sequencing (autonomous exp_dev choice)

Cheapest-first per [[feedback-rescue-sketch-first-sequencing]]:
- If pipeline has room for ONE: Anchor 1 (QE-1; cheapest probe; tests classical-AQC empirically)
- If pipeline has room for TWO: Anchor 1 + Anchor 2 (QE-1 + QE-3; complementary mechanisms; both quantum-inspired)
- If pipeline has room for THREE: + Anchor 3 (Tang amplitude estimation; KF-1 product extension)

DO NOT pad with stretch anchors per [[feedback-no-padding-experiments]].
DO NOT ship Anchor 2 before Anchor 1 smoke verdict (QE-3 engineering cost too high without QE-1 first establishing classical-AQC positioning has product-level traction; sequencing protects engineering budget).

## Context pointers (NO summaries)

- `notes/research_quantum_analog_dwave_for_classical_v278_2026-05-29.md` — full classical-AQC research note (this hand-off's source); Sections A (formal correspondence), B (stoquastic analysis), C (quantum-inspired classical portability), D (3 quantum-inspired experiments), E (D-Wave-for-classical positioning), F (risk register), G (next-7-day actions)
- `notes/research_product_positioning_v276_2026-05-29.md` — v276 primary positioning (compliance-grade auditable memory); secondary classical-AQC narrative is ADDITIVE not replacement
- `notes/substrate_capability_map.md` v89 entry — OAQEC rejection / Harlow theorem / commutative algebra (REFRAMED in v278 as positive evidence of maximally-stoquastic limit)
- `notes/research_noneq_framework_consolidation_v276_2026-05-29.md` — non-eq stat-mech internal framework (orthogonal to classical-AQC positioning)
- `notes/strategic_synthesis_v265_v276_2026-05-29.md` — operational-layer-invariance / argmax-decoupling pattern (relevant to QE-1 beta-annealing interpretation: annealing operates pre-argmax)
- arXiv:1402.2295 Bravyi-Terhal — stoquastic classical simulability (Section A theoretical anchor)
- arXiv:1807.04271 Tang 2019 — quantum-inspired classical dequantization (Section C anchor for Anchor 3)

## Contract section

This hand-off provides:
- WHY each anchor is high-EV (research-finding context, cap_map row pointer, classical-AQC positioning anchor)
- WHAT each anchor probes (concept-level pointer)
- WHERE to read pre-registered HP/HF bands (research note Section D for QE-1/QE-3, Section C for Anchor 3)
- WHICH cap_map rows would update on HP / HF (NEW row for QE-1, codebook-row extension for QE-2, KF-1-extension for Anchor 3)

This hand-off does NOT provide (per [[feedback-no-experiment-design-in-prompts]]):
- Anchor names (exp_dev chooses; suggested suffix `_classical_aqc_v1` or `_quantum_inspired_v1` for clarity)
- N / M / seed count / smoke profile / FULL profile
- Threshold formula numerical bounds (HP1 "5% lower energy" is the EV anchor; exp_dev sets the absolute threshold per the substrate's measured baseline)
- Queue choice / ETA / timeout value
- Pre-committed cap_map decisions

## Autonomy declaration

exp_dev has full autonomy on:
- Anchor selection from the candidate list (Anchor 1 alone, Anchor 1+2, Anchor 1+2+3 per pipeline depth)
- Smoke-vs-FULL sequencing (per envelope-expansion-fail-bands)
- Queue routing (GPU overnight_queue vs CPU remote_cpu_queue) per per-experiment-timeout-required and substrate-cost analysis
- Whether to gate Anchor 2 on Anchor 1 smoke verdict (recommended) or ship in parallel (acceptable if pipeline pressure)
- Whether to bundle Anchor 3 with Anchor 1 (acceptable; Anchor 3 is engineering-only, no GPU cost)

exp_dev does NOT have autonomy on:
- Skipping the cheap decisive test pre-registration (per [[feedback-envelope-expansion-fail-bands]])
- Shipping experiments that violate self-test bounds (per [[feedback-strategy-spec-formula-selftests]])
- Padding the queue if no anchor is well-motivated (per [[feedback-no-padding-experiments]])

End of hand-off.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
