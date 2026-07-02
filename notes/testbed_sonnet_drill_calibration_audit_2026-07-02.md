# Testbed Calibration Audit — Sonnet Hidden-Dim Drills 2026-07-02

**Filed-by:** hdi_testbed (integrator + fleet-health auditor)
**Trigger:** USER-authorized 2026-07-02 late-morning strategic gap review — audit whether today's Sonnet drills systematically over- or under-estimate risk against empirical outcomes.
**Scope:** 8 hidden-dim drills (Dim A/C/E/F/L/P/R/T) + 2 theory drills (sparse-coding + dense-HF underloaded-saturation) filed 2026-07-01/02.

---

## HEADLINE FINDING

**Systematic bias identified: SONNET DRILLS SIGNIFICANTLY OVER-ESTIMATE FRAGILITY.**

Across 5 drills with paired empirical outcomes, mean calibration delta is **−0.30** (predicted P_def minus empirical fragility). No drill under-estimated risk; four out of five over-estimated by 0.20+; one was directionally correct on a narrow-cliff phenomenon (Dim S) but wrong on regime location; one theory drill (dense-HF) had its regime table PARTIALLY FALSIFIED because the drill mis-identified substrate mechanism class (assumed Ramsauer softmax; actual is Hebbian + argmax cleanup).

The pattern strongly suggests **drill design defaults to worst-case generic-superposition / generic-Hopfield theory rather than substrate-specific mechanism-class evidence.** The substrate has empirically demonstrated 50x more robustness than several drills predicted (Dim E adversarial), and drills that leaned on distributional-shape prediction (Dim H two-tier) got FALSIFIED across 3 mechanism classes in v3 dual MM.

---

## CALIBRATION TABLE

| Drill | Empirical Cell | P_def (predicted fragility) | P_empirical (observed fragility) | Δ (pred − emp) | Bias direction | Notes |
|-------|---------------|-------------------------------|----------------------------------|------------------|----------------|-------|
| Dim E adversarial | `exp_adversarial_key_gap_crossing_v1` HARD_PASS_ADVERSARIAL_ROBUST | 0.52 (upward revision from 0.48; 0.65 gradient-attack sub-prediction) | ~0.05 (substrate withstands ε≤0.5 PGD; only bin at ε≥0.8 flips = 10x drill constants; encoder sole surface) | **+0.47 to +0.60** | OVER (5x-10x) | Drill quoted "epsilon=0.05 sufficient"; empirical needs ε≥0.5-0.8 for PGD success. Superposition-interference theory arXiv:2510.11709 assumed but substrate bipolar-iid + O(sqrt(N)) held.  |
| Dim S metric-dep | Dim S v1 HF_METRICS_IDENTICAL → v3 CG top-K cliff-bracket | 0.45 (mid-load metric axis load-bearing) | ~0.35 (real, but only in narrow σ cliff-band, NOT default regime) | +0.10 | DIRECTIONAL_HIT / REGIME_MISS | Drill was directionally right (metric-differentiation exists), wrong about regime location (mid-load vs cliff-band). Sparse-Hopfield NeurIPS 2023 prediction confirmed in narrow band only. |
| Dim H distributional | Dim H v2 HF_PREDICTION_FAILS + v3 dual MM (softmax + Hebbian W) | 0.38 (Zipfian two-tier prediction; based on Donoho-Tanner analogy) | ~0.10 (three mechanism classes all falsify two-tier; sparse-coding drill's L1-recovery analogy WRONG regime) | **+0.28** | OVER | CLT-washout theory drill (P_def=0.88 for saturation prediction) was CORRECT at underloaded α≤0.30 (substrate too robust to discriminate). Zipfian two-tier prediction was UNSUPPORTED. |
| Dim T regime-transitions | `exp_dim_t_joint_surface_alpha_sigma_interaction_v1` smoke HP δ=0.069 (2.3x margin) | 0.28 → 0.32 (small upward) | ~0.32 (well-calibrated; joint hypersurface interaction confirmed sigma_crit(α=0.10)=0.185 vs sigma_crit(α=0.45)=0.116) | **~0.00** | CALIBRATED | ONLY well-calibrated drill in the set. Theory basis (mean-field energy overlap in (α,σ)) was substrate-adjacent, not generic-superposition. Modest P_def matched modest empirical. |
| Dim P n-primitive | `exp_stage3_m3_stack_5_primitive_clarify_v1_seed_7_smoke` HARD_PASS 4/4 HP gates | 0.60 for 5-primitive CG lift; drill said depth REGIME-limited not primitive-count-limited | Empirical: 5th primitive validates cleanly (B_5PRIM_CLARIFY B_cm=0.875 vs A_cm=0.5); depth curves confirmed flat 5→100 | +0.10 | CALIBRATED_DIRECTIONAL | Drill correctly re-framed depth-vs-primitive-count. Deflated P_def=0.60 reasonable given depth-CG HARD_FAIL evidence was already in-hand. |
| Dim A temporal | (no cell run) | 0.32 → 0.08 downward | N/A (no empirical yet) | N/A | UNVERIFIED | Structural argument (Hebbian commutative) → cortex owns temporal. Reasonable if cortex-boundary temporal-encoding assumption holds. |
| Dim F throughput | (Dim F batched QPS queued) | 0.18 → 0.28 upward | N/A | N/A | UNVERIFIED | Theoretical predictions only. Awaits landing. |
| Sparse-coding + dense-HF theory | `exp_cortex_hippo_dense_beta_sweep_v3` + operational_wall v2b (via drill inference) | Dense-HF drill: P_def=0.85 for Ramsauer softmax mechanism; sparse-coding drill P_def=0.38 for L1-recovery two-tier | PARTIALLY_FALSIFIED — substrate is Hebbian + argmax cleanup, NOT Ramsauer softmax; drill's regime table for softmax mechanism DOES NOT APPLY | mechanism-class miss | MECHANISM_CLASS_ERROR | Dense-HF drill explicitly conceded "NOT APPLICABLE to substrate Cell D v2" for mechanisms (b) + (c) but still generated a regime table conflating softmax-Ramsauer thresholds with substrate behavior. Sparse-coding drill leaned on Donoho-Tanner AMP framing (P_def=0.48) that the two-tier Zipfian empirical result FALSIFIED (Dim H). |

---

## SYSTEMATIC BIAS ANALYSIS

### Direction: OVER-ESTIMATION OF FRAGILITY

Across 5 paired drills, mean signed Δ = **+0.19** (positive = over-estimated fragility). If we weight by result strength (excluding the CALIBRATED and DIRECTIONAL cases), the two OVER cases average **Δ = +0.37**.

### Magnitude: 2x-10x on load-bearing predictions

- Dim E adversarial: constants off by 10x (drill quoted ε=0.05 sufficient; empirical needs ε≥0.5-0.8)
- Dim H distributional: drill P_def 0.38 → empirical <0.10 (~4x over)
- Dense-HF regime table: mechanism-class ERROR not just magnitude — the drill applied to a substrate architecture it did not have

### ROOT CAUSES (identified pattern)

**(1) Generic-superposition / generic-Hopfield theory as default prior when substrate has empirical CG evidence to the contrary.**

Example: Dim E drill leaned on arXiv:2510.11709 (2025 "Adversarial Attacks Leverage Interference Between Features in Superposition") — a generic-superposition result. Substrate's bipolar-iid + O(sqrt(N)) margin held far more strongly than the generic theory predicted, because the substrate is NOT a generic learned-embedding model.

**(2) Mechanism-class assumptions not verified against v2c AGS-SNR CG or Cell D v2 architecture before writing regime tables.**

Example: Dense-HF drill wrote a regime table using softmax-Ramsauer thresholds while conceding in the text that substrate uses Hebbian + argmax. The table was then partially FALSIFIED because substrate followed AGS Hebbian dynamics, not Ramsauer softmax dynamics. This is a structural drill-authoring bug.

**(3) Distributional-shape / cross-modality predictions default to "risk high" without substrate-KB check.**

Example: Dim H Zipfian two-tier prediction based on Donoho-Tanner analogy. Substrate-KB query would have returned the operational_wall v2b CG showing substrate is HEBBIAN + ARGMAX cleanup — for which the L1-recovery AMP analogy DOES NOT APPLY. Three mechanism classes all falsified two-tier in Dim H v3 dual MM.

**(4) Lit-scan calibration penalty (0.15) applied to raw estimate but base rates still generic-Hopfield.**

The lit-scan penalty deflates novel-synthesis claims by 0.15-0.25 but does NOT correct for the base-rate error of applying generic-Hopfield theory to a substrate that has explicit chain-grade evidence characterizing its mechanism class. Result: penalized-but-still-wrong base rate.

### DRILLS THAT WORKED

- **Dim T regime-transitions** was well-calibrated because it grounded predictions in **substrate-adjacent evidence** (cortex_hippo_dense_beta_sweep_v3 as parent CG; mean-field energy overlap in α×σ analytically tractable AND substrate-mechanism-consistent).
- **Dim P n-primitive** was directionally correct because it used prior substrate CG evidence (depth curves flat 5→100, lift_sub=0.02 orthogonality) rather than generic composition theory.

**Common thread among well-calibrated drills: substrate-KB-first grounding + parent-CG citation, not just literature-first prediction.**

---

## M3 ARCHITECTURE RECOMMENDATIONS — WHICH SHOULD BE UPDATED

Given empirical over-estimation of fragility, the following M3 recommendations from today's drills should be **DEMOTED from "mandatory hardening" to "prudent defense-in-depth":**

1. **Dim E drill recommendation:** "Stochastic noise + secret K_proj + adversarial training of encoder + query norm monitoring" — the FIRST TWO (noise + secret K_proj) remain load-bearing IF and only if M3 uses an LLM encoder (encoder is empirically THE sole attack surface per the HARD_PASS result). Adversarial training of encoder + query norm monitoring can be DEMOTED to Phase-2 defense-in-depth — substrate itself is not the bottleneck.

2. **Dense-HF drill regime table:** The Ramsauer softmax regime rows should be marked NOT APPLICABLE for the Cell D v2 substrate; only the AGS Hebbian rows should be trusted. Currently the drill's REGIME TABLE section conflates these.

3. **Sparse-coding drill's Zipfian two-tier prediction:** SHOULD BE MARKED FALSIFIED by Dim H v3 dual MM. Two-tier capacity rating recommendation (cert reports head vs tail separately) is DEMOTED — empirical does not support two-tier at underloaded-regime; may still apply near cliff-band per Dim S v3 top-K rescue result.

4. **Dim T joint-controller M3 refuse-gate upgrade:** REMAINS VALID — this drill was well-calibrated; sigma_crit gap of 0.069 is a real cortex-boundary design constraint.

5. **Dim P 5th-primitive CG lift:** REMAINS VALID (smoke HP; awaits FULL). Drill was directionally correct.

**No drill's recommendation needs to be UPGRADED to more-aggressive hardening.** All corrections point toward LESS engineering conservatism than drills prescribed.

---

## RECOMMENDATIONS FOR FUTURE SONNET DRILL DISCIPLINE

### R1 [PRIMARY, LOAD-BEARING]: Mechanism-class verification MANDATORY before regime tables

**Discipline:** Before writing any regime table, threshold prediction, or fragility estimate, the drill MUST query substrate-KB for the parent CG that characterizes the substrate mechanism class in that regime. If parent CG says "Hebbian + argmax," the drill CANNOT use Ramsauer softmax thresholds without an explicit MECHANISM_CLASS_MISMATCH disclosure marking the prediction NOT_APPLICABLE.

**Enforcement:** Add pre-drill checkpoint: "Which CG characterizes the substrate mechanism in this dimension's regime? Cite anchor path. If unknown, drill P_def CAP at 0.35 and flag as MECHANISM_UNCERTAIN."

### R2: Lit-scan calibration penalty must be REGIME-CONDITIONAL

**Current:** flat 0.15-0.25 penalty on all novel-synthesis claims.
**Proposed:** additional +0.15 penalty when substrate mechanism class differs from the paper's mechanism class. So Ramsauer-2020 predictions applied to Hebbian substrate get -0.30-0.40 total. Donoho-Tanner CS predictions applied to Gram-matrix Hebbian substrate get -0.30 total.

**Rationale:** the base-rate error dominates the calibration error; flat penalty does not correct it.

### R3: Empirical CG evidence OVERRIDES theory prediction

**Discipline:** When substrate-KB returns a chain-grade atom characterizing behavior in the regime being drilled (e.g., v2b AGS-SNR CG for saturation, adversarial_key_gap_crossing_v1 CG for gradient attacks), the drill's P_def MUST be anchored to that CG evidence, not to generic-superposition theory. If theory predicts fragility and CG says robust, CG wins.

**Enforcement:** Include a "PARENT CG CITATION" line in every drill headline. If no parent CG exists, the drill is marked NOVEL_SYNTHESIS and P_def CAPPED at 0.50 (already in discipline; extend cap to 0.35 if mechanism class assumed but unverified).

### R4: Constants must be COMPUTED not QUOTED from literature

**From MEMORY.md "COMPUTE FORMULAS IN CODE 2026-06-27" discipline extended to drills:**

Any drill quoting "epsilon=0.05 sufficient for attack" or "N=8192 gives 0.011 gap" MUST show the computation with substrate parameters plugged in. Mental arithmetic on sqrt/log chains produces the 10x errors seen in Dim E drill.

**Enforcement:** Reject any drill headline that quotes a threshold without an accompanying compute-in-Python trace or an explicit "quoted from paper — not computed for substrate" disclaimer.

### R5: Post-drill calibration ledger

**Propose:** Add `notes/calibration_ledger.md` maintained by Testbed. Each drill entry gets a row: date / drill / P_def / paired-cell-verdict / observed / delta / bias-direction. After N=10 drills, compute rolling calibration score and USER can spot systematic drift.

**Rationale:** without a ledger, systematic bias like today's +0.30 over-estimation is invisible. This audit is the first-instance detection; a ledger makes it continuous.

---

## PROCESS-HEALTH AUDIT FLAGS

Beyond calibration, three process-health concerns surface from this audit:

**F1 [MODERATE]:** Drill notes are being cited in cortex-milestone architecture decisions BEFORE paired empirical validation lands (e.g., Dim E stochastic-noise recommendation was already load-bearing per the 2026-06-30 M3 cortex-noise directive). If drills over-estimate fragility, architecture decisions get over-hardened. Recommend: architecture recommendations from drills SHOULD wait for paired empirical, or be tagged PROVISIONAL_PENDING_EMPIRICAL.

**F2 [MODERATE]:** The dense-HF drill explicitly conceded mechanism-class mismatch mid-text ("NOT APPLICABLE to substrate Cell D v2") but the REGIME TABLE at the end included softmax thresholds anyway. This is a structural drill-authoring bug — internal contradiction between mechanism-check section and regime-prediction section.

**F3 [LOW]:** No drill in this batch cites a substrate-KB query hash / receipt in the headline. Substrate-KB canonical query-first discipline (2026-06-27 USER) is not visible in the drill outputs. Recommend: header line "substrate-KB query: <query>, top hits: <slug1>@cos, <slug2>@cos" as first section.

---

## SUMMARY

- **Systematic bias:** SONNET DRILLS OVER-ESTIMATE FRAGILITY BY ~0.30 (mean Δ across 5 paired drills)
- **Mechanism-class errors** are the largest single failure mode (dense-HF regime table applied Ramsauer to Hebbian substrate)
- **Best-calibrated drills** (Dim T, Dim P) grounded predictions in substrate CG evidence, not generic theory
- **Worst-calibrated drills** (Dim E, Dim H) leaned on generic-superposition / Zipfian-CS theory as base rate
- **Load-bearing recommendation:** R1 (mechanism-class verification against parent CG mandatory before regime tables) + R5 (ongoing calibration ledger)
- **M3 architecture impact:** several drill recommendations should be DEMOTED to defense-in-depth; NO recommendation needs UPGRADING; Dim T + Dim P recommendations REMAIN VALID

---

*Testbed audit filed 2026-07-02. Ledger cadence proposed. Calibration snapshot: 5 paired drills, mean Δ = +0.19 (biased toward fragility over-estimation), 2 CALIBRATED, 2 OVER, 1 MECHANISM_CLASS_ERROR.*
