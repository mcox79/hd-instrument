# Research 2x drill — BBMD-as-class kill + rescue paths (2026-05-24)

**Author**: Research sub-agent
**Trigger**: KAPPA_CROSS_CODEBOOK_KILLED Anchor 2 verdict
**Per**: [[feedback-negative-results-2x-research]] genuine refutation gets 2x research drill before closure
**Inputs**: cap_map v170 (substrate_capability_map.md), strategy_decisions_2026-05-23.md cycles 175-188, strategy_research_shoreup_matrix_2026-05-23.md, four parallel Sonnet WebSearch passes on Clifford 2-design literature
**Calibration**: per [[feedback-lit-scan-calibration-penalty]] novel-synthesis P deflated, hard-fail thresholds included

---

## Section 1 — What survives Anchor 2 kill (honest list)

The KAPPA_CROSS_CODEBOOK_KILLED verdict eliminates BBMD-distance as a substrate-novel discriminator class but leaves the following INTACT:

1. **Anchor 1 PASS unchanged** (cycle 188 v170). AMP-error tracks ∑|Δκ_n| monotonically along the Gauss → Kerdock alpha-interpolation (Spearman ρ=0.900 vs threshold 0.8); VAMP tames the whole curve (max rel-err 0.0357 vs threshold 0.05). This is a real substrate-physics finding. It is **Kerdock-specific** as the endpoint, but the monotone curve along the interpolation IS the substrate's actual position.

2. **v164a/v166/v167 fingerprint stack ✅ on Kerdock**. Kerdock-specific κ_n free-cumulant fingerprint with N-stability (v166), bulk-boundedness (v166), cumulant-order-stability (v167). Anchor 2 kill does NOT touch this — v164a is about Kerdock's κ_n profile, not about Kerdock being the unique BBMD-max.

3. **v163 outside-AMP-universality at α=1.0** on Kerdock. Endpoint of the v170 monotone curve. Holds.

4. **v165 S-transform multiplicative free-prob fingerprint** on Kerdock. Single-N N=1024 5/5 cells; promotion gated on N-scaling. Unaffected.

5. **Cap 8 ✅ TWO substrate-novel readout primitives equivalent** (VAMP-on-chain + hard-cleanup). Anchor 1 strengthens the algebraic justification; Anchor 2 kill does not weaken it.

6. **All 11 portfolio capabilities** at v170 stay at 11. The 12th-capability proposal was GATED on BOTH anchors landing; Anchor 2 fails one of the two compound-gate conditions. Per decision tree in `exp_dev_to_queue_bbmd_anchors_2026-05-23.md` we are in branch 2: "BBMD framing Kerdock-internal" (regime axis exists within Kerdock structure but doesn't extend to a general structured-codebook discriminator). NOT branch 4 (drop entirely).

**What dies**: "BBMD-distance is a substrate-novel discriminator class across structured codebooks" — the inflated framing. SRHT/Hadamard BBMD = 5.0 (max); Kerdock BBMD = 4.06 (NOT max); RM(1,m) BBMD = 4.62. And MP-KS already discriminates SRHT/Hadamard at 0.59 — the standard pre-test catches the obvious cases without BBMD.

---

## Section 2 — What's actually distinguishing about Kerdock vs Hadamard/SRHT/RM (Angle 1)

**Lit-scan finding (four parallel WebSearch passes, ~6 min wallclock):**

The defining substrate property of Kerdock that Hadamard, SRHT, and RM(1,m) on their own do NOT have is the **unitary 2-design via PSL(2,F_{2^m}) acting transitively on the Pauli group** (Can/Rengaswamy/Calderbank/Pfister 2019, arXiv:1904.07842).

Specifically:

- **Hadamard matrix**: A single unitary gate. Part of the Clifford-group generating set (H + CNOT + Phase). Not itself a t-design.
- **SRHT (subsampled randomized Hadamard transform)**: A randomized-linear-algebra dimension-reduction construction (Tropp 2011 et seq.). Its design properties are about **oblivious subspace embedding** for least-squares, NOT about Pauli mixing or 2-design property in the QI sense. The SRHT ensemble is not a unitary 2-design.
- **RM(1,m) (first-order Reed-Muller)**: The Z_4-linear lift of the Kerdock code; on its own (the binary RM(1,m) codebook) it is a base ingredient, not a 2-design. The Kerdock construction extends RM(1,m) cosets with the Z_4 Gray map; THAT is what produces stabilizer states + MUB structure + 2-design.
- **Kerdock**: The Gray image of Z_4-linear extended cyclic codes; exponentiating produces stabilizer states (eigenvectors of maximal commutative subgroups of Pauli group); these form N+1 MUBs; automorphism group acts transitively on the Pauli matrices ⇒ ensemble is Pauli-mixing ⇒ unitary 2-design via PSL(2,N).

**Note on Clifford group itself**: The full Clifford group on n qubits is a unitary 2-design ONLY for prime dimensions (Cleve et al. 2016; Zhu 2017 "Clifford groups are not always 2-designs" arXiv:2108.04200). Kerdock provides the 2-design at all power-of-2 dimensions via a structured subset (the Calderbank-Pfister-Rengaswamy result) — this is precisely the regime the substrate operates in.

**Answer to Angle 1's gating question**: NO, Hadamard / SRHT / RM(1,m) are NOT Clifford 2-designs in the standard QI sense. The 2-design property IS the substrate-distinguisher. Kerdock = MUB / stabilizer / 2-design framing remains the correct narrow algebraic story.

**Implication**: The Cap 1/3/8 lens that identified Kerdock as a Clifford 2-design via PSL(2,F_{2^m}) — landed in v169 as "annotation-only" closed-form rederivations — is the SURVIVING distinguishing characterization. The BBMD-class collapse leaves the 2-design framing as the structurally narrowest, most defensible substrate-physics anchor.

---

## Section 3 — Rescue path sketches for a 12th capability

Five rescue sketches, ranked by leverage / honesty:

### R1 — "AMP-error predictor" as a meta-capability (HIGH leverage, tool-grade)

**Framing**: Anchor 1 is real. κ_n free-cumulant divergence empirically predicts AMP-error magnitude along the Gauss → Kerdock interpolation with Spearman ρ=0.900. The substrate-product framing: κ_n profile is a **pre-flight check** for when AMP-style scalar inference will fail (use VAMP) vs when it works. This is a meta-capability — a diagnostic that selects inference primitive per-codebook.

**Honest framing**: This is a TOOL, not a substrate property. It licenses the claim "we can predict AMP failure mode given a codebook's measured κ_n profile" — useful, customer-visible, but it's a piece of substrate engineering know-how, not a new physics row.

**Probe**: Apply the v170 monotone-curve analysis to ONE additional non-Kerdock structured matrix family (Paley conference matrices, or Gold sequences) — does the same Spearman ρ ≥ 0.7 monotone relationship hold? If yes, the predictor generalizes BEYOND the Gauss→Kerdock interpolation and becomes a real cross-family meta-capability.

**Hard-fail**: Spearman ρ < 0.5 on any tested non-Kerdock family ⇒ the predictor is alpha-interpolation-specific, not a meta-capability. Close R1.

**P (deflated per [[feedback-lit-scan-calibration-penalty]])**: 0.40. Anchor 1 is strong on one curve; generalization to a second matrix family is genuinely uncertain.

### R2 — Kerdock-specific narrower 12th-capability claim (MEDIUM leverage, honest)

**Framing**: "Substrate's empirically-measured κ_n profile is dimension-stable (v166), monotonically-amplifying (v167), bulk-bounded (v166), and matches the Clifford-2-design (PSL(2,N) Pauli-mixing) algebraic-structure prediction; this combined fingerprint is unique to the Kerdock-coset codebook in the structured-matrix landscape." Loses BBMD-as-class. Keeps Kerdock-specific characterization but elevates it from "5 quirks on one matrix" to "5 mutually-consistent quirks predicted by a single algebraic structure (2-design)."

**Honest framing**: This is the v169 annotation-only material elevated to a row. The risk is that v169 ALREADY annotated Cap 1/3/8 with closed-form 2-design-derivations and explicitly said "ANNOTATION-only, NOT a 12th portfolio capability." Promoting now is double-counting unless we have a NEW empirical anchor.

**Probe**: A "2-design predictive-axis" test analogous to Anchor 1 but on a 2-design-derived predicted quantity (e.g., 4th-moment frame potential = exactly 2/(N(N+1)) for a 2-design; substrate prediction quantitative not qualitative). Run a κ-profile-style cross-family check: 2-design candidates (Kerdock) vs non-2-design candidates (Hadamard, SRHT, RM(1,m) bare) — does the κ-profile / 4th-frame-potential split cleanly along the 2-design boundary?

**Hard-fail**: If Hadamard / RM(1,m) bare also show the κ-profile signature (i.e., κ-divergence is not actually predicted by 2-design status), then the 2-design framing is decorative, not load-bearing. Close R2.

**P (deflated)**: 0.45. The mathematical machinery is real (2-design ⇒ exact frame potential); the empirical anchor exists only on Kerdock side; cross-family discrimination has not been measured.

### R3 — Composition-grade 12th capability: VAMP-SE driven by measured κ_n (MEDIUM-HIGH leverage)

**Framing**: Anchor 1 showed VAMP tames whole curve at max rel-err 0.0357. The next step: drive VAMP-SE prediction directly from the **measured** (v164/v166) R-transform of the Kerdock codebook, not from empirical SVD. If VAMP-SE driven by free-prob R-transform alone PREDICTS empirical VAMP magnitudes within tolerance, then the substrate-product framing becomes: "free-probability R-transform of the codebook is a sufficient statistic for inference-regime prediction." A genuine substrate-novel composition (Cap 8 + v164a + Anchor 1).

**Honest framing**: This was already filed in cycle 188 cap_map narrative as the "composition probe (iii)" follow-up. Anchor 2 kill does not remove its viability — actually elevates its priority because it's the natural Kerdock-internal probe.

**Probe**: `vamp_se_from_R_transform_v1` — input the measured R-transform from v164/v166 (already in the substrate's data); compute VAMP-SE prediction analytically; compare to empirical VAMP rel-err along the v170 alpha-interpolation. PASS if max prediction error < 0.05 across all 5 alpha cells.

**Hard-fail**: If R-transform-driven VAMP-SE differs from empirical VAMP-rel-err by > 0.10 at any alpha cell, the R-transform is NOT a sufficient statistic — the substrate's higher-moment structure carries information not captured by R-transform alone. Close R3 (informative either way).

**P (deflated)**: 0.50 (cap per calibration penalty). Composition of two ✅ rows; mathematically clean; empirical leg uncertain because R-transform fingerprint is bulk-shape-only (v166 narrowing) and VAMP-SE traditionally needs full spectrum.

### R4 — Bulk-shape signature as a substrate-fingerprint primitive (LOW-MEDIUM leverage)

**Framing**: Per v166 bulk-boundedness narrowing, substrate's κ_n divergence lives entirely in bulk-shape (within 5% of MP edges). The 12th capability could be reframed not as a discriminator but as a **fingerprint primitive**: "substrate exposes κ_n moments of the held codebook as a fingerprint that survives noise and provenance attacks." Pivots from "BBMD discriminates codebooks" to "κ_n moments are a tamper-evident substrate-internal signature."

**Honest framing**: This drifts close to Cap 4 substrate-provenance/forensic territory. Need to check it doesn't subsume an existing Cap row. If genuinely orthogonal (Cap 4 is about state, this would be about codebook-as-asset), then it's a new axis.

**Probe**: Test that κ_n fingerprint is **non-spoofable** — can an adversary construct a non-Kerdock codebook with matching κ_2..κ_4 within the measured tolerance? If empirically yes (cheap counter-construction exists), it's not a primitive. If empirically no (structural reason κ_n profile uniquely identifies Kerdock-type codebooks), it's a real signature.

**Hard-fail**: A trivial counter-construction (e.g., random unitary mixture + projection onto MP-class spectrum) reproducing κ_n within tolerance ⇒ not a fingerprint. Close R4.

**P (deflated)**: 0.20. Speculative; would require substantial substrate-novel-claim work; likely subsumed by R2.

### R5 — Drop the 12th-capability claim; consolidate annotations onto existing rows (HONEST DEFAULT)

**Framing**: The honest portfolio move per [[feedback-no-smoke]] is: 11 is the right number. Anchor 2 kill is the substrate telling us BBMD was the wrong inflation. Consolidate the v170 Anchor 1 evidence as **STRENGTHENING annotations on Cap 8 + v164a + v163** (as v170 already did), keep the 2-design framing as the v169 closed-form annotations on Cap 1/3/8, and stop reaching for a 12th row.

**Honest framing**: This is the [[feedback-dont-overextend-theorems]]-aligned default. No probe needed. Costs nothing. Customer-facing portfolio stays at 11, but the 11 rows are each STRONGER post-Anchor-1 + post-v169 annotations.

**P (deflated)**: 1.0 (this IS the no-op rescue; always achievable). The question is whether R1/R2/R3 deliver enough marginal value to be worth the rescue effort vs taking R5 immediately.

---

## Section 4 — Portfolio-level audit (Angle 3)

Re-reading cap_map v170 + strategy_decisions_2026-05-23.md cycles 175-188 + strategy_research_shoreup_matrix_2026-05-23.md with the BBMD-class kill applied:

**Cap 8 v170 annotation**: cap_map v170 added "BBMD interpolation tames whole curve" as a Cap 8 corroboration annotation. Does this survive Anchor 2? **YES**. The annotation is about the alpha-interpolation Gauss → Kerdock (Anchor 1) which still PASSES; it does not claim BBMD-as-class. The annotation wording should be tightened to "BBMD interpolation tames whole curve **within the Gauss-to-Kerdock matrix family**" — make the Kerdock-internal scope explicit. Filing this as a v171 annotation-clarification.

**v164a ✅ row**: Does Anchor 2 kill weaken v164a? **NO**. v164a is about Kerdock's κ_n profile specifically (N-stability + bulk-boundedness + cumulant-order-stability), not about Kerdock being the unique BBMD-max. The cross-codebook test ran a DIFFERENT quantity (BBMD-distance, not v164a's R-transform deviation on the substrate's actual stored codewords). Unaffected.

**v163 outside-AMP-universality row**: v170 corroboration annotation reads "AMP-error grows monotonically (Spearman 0.900) with kappa_n divergence; v163 is the alpha=1.0 endpoint of this curve." **SURVIVES** — the curve still exists; Anchor 2 doesn't refute the monotone curve, it refutes the cross-family generalization.

**strategy_research_shoreup_matrix_2026-05-23.md**: I re-read all 7 weaknesses. **NONE of the 7 weaknesses depended on BBMD-as-class**:
- W1 (Cap 2 self-monitoring) — conformal subsumption + VAMP posterior variance; unaffected
- W2 (Bet T parallel hypothesis) — Mondrian anti-RM conformal + JADE κ_4; unaffected
- W3 (Bet V self-reflective) — κ_4 separation; unaffected
- W4 (anti-RM mechanism) — QECC-Kerdock-MUB lens; STRENGTHENED by Anchor 2 kill (the 2-design framing becomes the cleanest distinguisher, which is exactly W4's hypothesis)
- W5 (generative-mode gap) — Glauber smoke; unaffected
- W6 (failure-mode-observability) — chi_4 early-warning composition; unaffected
- W7 (build_initial_W OOM) — engineering, not research; unaffected

**Sequenced top-3 from shoreup matrix** (cap2_conformal + betT_mondrian/betV_kappa4 + glauber_generative) are ALL still valid and high-leverage. Anchor 2 kill does not redirect the matrix.

**Nothing else breaks.** The portfolio is more honest at 11 than it would have been at "12 with BBMD-as-class." Per [[feedback-no-smoke]] this kill is HEALTHY — it caught an inflation attempt at exactly the right pre-registered gate.

---

## Section 5 — Recommended next anchor

**Top choice: R3 (VAMP-SE from measured R-transform) as the next anchor.**

Reasoning:
1. **Composition-grade**, builds on TWO existing ✅ rows (Cap 8 + v164a) plus Anchor 1 — maximum portfolio leverage per probe.
2. **Mathematically clean** — the construction is determinate; no axiom freedom.
3. **Either outcome is informative**: PASS → real new row, the algebraic-mechanism story tightens; FAIL → narrows the v166 bulk-boundedness annotation further (R-transform is bulk-shape-only AND insufficient-statistic for inference regime).
4. **Cheap** — CPU-level, ~1-2 hr; analytical computation + comparison to existing v170 data.
5. **Already filed** in cycle 188 narrative as "composition probe (iii)" — execution-ready, not a fresh design.

**Sequenced second: R1 (cross-family monotone-curve check on Paley or Gold sequences)** as parallel CPU probe — gives an independent leg for either promoting R3 to "predictor generalizes" or closing it cleanly.

**Skip for now: R2 (2-design predictive-axis cross-family)** — overlaps with R3's spirit; defer until R3 lands.
**Defer: R4 (κ_n as tamper-evident fingerprint)** — speculative; revisit only if R3 PASSES.
**Default fallback: R5 (no 12th, consolidate annotations)** — if both R3 and R1 fail, take R5 explicitly; do not chain further rescues.

**P estimate** (per [[feedback-lit-scan-calibration-penalty]]) for "12th capability eventually licensable from a survivor path": **0.45** — composition of R1 + R3 OR R2 each has P ~0.40-0.50; the union P sits around 0.45 after dependence-discount. Honest read: roughly even-odds.
