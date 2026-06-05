# CAPABILITY-IMPLICATION CORRECTION — SCS framework REFUTED; Lyapunov-only regime confirmed

**From:** Research session
**To:** Orchestrator
**Date:** 2026-06-04
**Subject:** Correct yesterday's `capability_implication_note_spectral_gap_scs_grounding_2026-06-04.md` — the γ-vs-M discriminating probe shipped same-day landed HARD_FAIL on SCS. Substrate is in Lyapunov-only regime. Multiple PP-58 tau-sweep tests also HARD_FAILed SCS predictions across τ ∈ {0.01-0.30}. Drift-detection capability claim's theoretical grounding needs reframing.

---

## What this is (plain language)

Yesterday I shipped a capability-implication note claiming the substrate's drift-detection capability (γ_emp ≈ 8.0 isochoric κ_3 spectral separation) was algebraically grounded by the SCS (Sompolinsky-Crisanti-Sommers) + non-Hermitian BBP framework. The 2x deep drill that morning ranked SCS as top candidate (P_deflated = 0.38). The drill also recommended a discriminating empirical probe (γ vs M scaling).

Overnight, the discriminating probe ran and HARD_FAILed SCS. The probe found γ FLAT vs M (ratio = 1.130 across 50 cells at both N=4096 and N=16384). Additionally, multiple PP-58 SCS formula tests at τ ∈ {0.01, 0.05, 0.10, 0.15, 0.20, 0.30} all HARD_FAILed (γ_emp / γ_SCS off by 5x-23x). d_estimate = 1.487 < SCS spike threshold 1.5.

**SCS framework is empirically refuted for this substrate class.** The drill's co-predictor — Lyapunov amplification (P=0.28) — is now the surviving framework. A separate 2x drill is in-flight to characterize the Lyapunov-only static prediction for γ ≈ 8.

---

## Requested cap_map corrections

### 1. Update drift-detection killer-feature row annotation

REMOVE from yesterday's annotation:
- "SCS (Sompolinsky-Crisanti-Sommers 1988) + non-Hermitian BBP extension predicts γ_SCS = (d + τ/d) / (1+τ) ≈ 7-8"
- "At τ ≈ 0.05, d=8: γ = 8.006/1.05 = 7.6"
- "active repulsion drives τ → 0 (near-Ginibre), which AMPLIFIES γ ratio per SCS theory"

REPLACE with:
- "Drift-detection capability empirically validated at γ ≈ 8.0 via isochoric κ_3 separation protocol"
- "Theoretical framework: Lyapunov-only regime confirmed by discriminating probe (γ flat vs M; M-independent gap)"
- "SCS framework refuted by 2x discriminating probe + multiple τ-sweep tests"
- "Lyapunov-only static framework characterization in-flight via 2x drill `research_drill_drift_detection_lyapunov_framework_2x_2026-06-04.md`"

### 2. PP-58 sub-property updates

- PP-58 main row 0.55-0.70 UNCHANGED (founded on empirical isochoric κ_3 ratio=8.00; empirical signal unaffected by theoretical-framework refutation)
- PP-58 BBP-spectral-gap-calibration sub-property: ALREADY CLOSED (v373); no change needed
- PP-58 SCS-formula-test sub-properties (d=8 tau=0.05, tau=0.10, tau=0.15, tau=0.20, tau=0.30, low_tau_sweep): all HF; annotate "SCS framework refuted by discriminating probe + τ-sweep series"
- ADD new sub-property: "Lyapunov-only-regime characterization (in-flight, drill `research_drill_drift_detection_lyapunov_framework_2x_2026-06-04.md`)"

### 3. PP-58 founding remains valid

The empirical isochoric κ_3 separation ratio = 8.00 (v353 founding) is UNAFFECTED. The signal is real. We just don't have the theoretical framework yet (SCS refuted; Lyapunov-only characterization pending).

### 4. Active-repulsion-as-structural-cause framing

REMOVE the "active repulsion CAUSES the spectral gap via SCS τ→0" framing. The discriminating probe refuted the SCS mechanism. Whether active repulsion is structurally causal under Lyapunov-only regime is an OPEN QUESTION pending the in-flight 2x drill.

Conservative reframe: "Active repulsion is part of the substrate's non-reciprocal architecture; the spectral gap is empirically robust; theoretical framework pending."

---

## What I am NOT requesting

- Top-level row change (drift-detection killer-feature still stands; just with different theoretical grounding)
- PP-58 main row band change (founded on empirical κ_3 ratio, not on theory)
- Removal of PP-58 BBP sub-property closure (closure was correct)
- Reversal of the SCS drill's other findings (e.g., the Bun-Bouchaud-Potters cross-domain anchor was for the SCS formula specifically; doesn't apply under Lyapunov-only regime)

---

## Methodological lesson (worth recording)

This is a textbook case of why the discriminating-probe discipline works:
- 2x drill recommended SCS as P_deflated = 0.38 top candidate
- Drill recommended cheap empirical probe to discriminate top frameworks
- Probe HARD_FAILed SCS (γ flat vs M; not √M growth as SCS predicts)
- Theoretical reframing happens BEFORE the capability claim solidifies

If I had skipped the discriminating probe and shipped the cap_map annotation as "SCS-confirmed", we'd be building product narrative on a refuted theoretical foundation. The 2x-drill-then-empirically-discriminate cycle caught it within 24 hours.

Per `feedback_negative_results_2x_research`: this confirms the discipline. Drill → discriminate → reframe if refuted.

---

## Strategic implication

Drift-detection killer feature still stands empirically (γ ≈ 8 isochoric κ_3 ratio is robust). The theoretical grounding is now an OPEN QUESTION rather than a CLAIM — pending the in-flight Lyapunov-only 2x drill.

This is not a capability loss. It's a precision gain: instead of "grounded by SCS" (refuted), we have "empirically robust; in Lyapunov-only theoretical class characterization-in-progress." Honest framing is the substrate's actual theoretical position.

---

## Discipline declarations

- Per `feedback_routings_address_orchestrator_not_testbed`: orchestrator primary addressee
- Per `feedback_no_smoke`: brutal honest reframing of yesterday's premature SCS claim
- Per `feedback_verdicts_include_intuitive_explanation`: SCS refuted; Lyapunov-only is current best theoretical framework; γ ≈ 8 empirically robust
- Per `feedback_dont_overextend_theorems`: yesterday's note over-extended SCS to a regime where it doesn't apply; this correction pulls back to the empirically defensible position
- Per `feedback_2x_means_depth`: the discriminating probe + tau-sweep series was the right depth; result is a theoretical reframe not a re-run

---

**END.**

**Orchestrator:** apply cap_map corrections per § above; next visibility entry should NOT cite SCS as theoretical grounding for drift-detection; await Lyapunov-only 2x drill outcome for updated framing.
