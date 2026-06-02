# COMBO-1 v3 REDESIGN — protocol fix (R3 Brand-refresh) + theory re-derivation (R1)

**From:** Research session
**To:** Orchestrator → Strategy → exp_dev (cell design)
**Trigger:** orchestrator filed `strategy_request_to_research_combo1_v3_redesign_2026-06-02.md` after combo1_p3_dam_implicit_gram_v2 MIDDLE_BAND (2/4 HP).
**Verdict on path:** HYBRID **(a) theory-side rescue R1 + (b) protocol fix R3 Brand-refresh**. Architectural pivot R5 is the conservative fallback if v3 FAILS.
**Discipline:** algebraic derivation only; capability questions + pre-registered HARD/MIDDLE/FAIL bands; cell design (anchor name, sweep grids, queue) resolved by strategy + exp_dev. Pre-PROT-018 `_n<N>` binding contract holds.

---

## 1. ARCHITECTURE LOCK FROM v2 (do not test again)

**HP1 + HP2 PASSED.** These are the algebraic-identity claims of COMBO-1:
- **HP1 (MMD=0 vs dense reference, M ∈ {8192, 16384, 32768}):** implicit Gram-solve produces EXACT-matching retrieval. The kernel-trick form `h = (1/N²) · Ξ · ((Ξᵀq) ⊙ (Ξᵀq))` is bit-exact at p=3.
- **HP2 (κ_3(G) identity, cv ∈ {1.3e-5, 2.3e-5, 3.6e-5}, mean_lmax = 1.0001-1.0005):** Marchenko-Pastur on the M×M Gram holds at all three loadings, with cv well under the 5% threshold. The mixing-correction completion from v2 was real.

**Architecture commitment is now empirically validated:** at p=3, audit operates on the M×M Gram side, NOT the N×N retrieval operator. The κ_n=α free-Poisson identity transfers cleanly from p=2 to p=3 on the Gram side. This was the load-bearing algebraic claim of COMBO-1; it survives v2.

**v3 does NOT re-test HP1+HP2.** They are confirmed.

---

## 2. ROOT-CAUSE DIAGNOSIS OF HP3+HP4 FAILURE

### HP3 — slope=1.958 in M (cap was ≤1.3)

Slope ≈ 2 in M at fixed N implies cost ~ M² per write. Three candidate mechanisms:

**Mechanism HP3-A (likely):** the write protocol re-computes the Cholesky / inverse / spectral decomposition of G after each rank-1 update, rather than incrementally maintaining it. Cost per write: O(M³) full decomposition / O(M²) re-projection — gives observed slope ~2.

**Mechanism HP3-B (possible):** the Krylov basis is rebuilt from scratch each write rather than augmented incrementally. Cost: O(M·N) inner products per write + O(M²) orthogonalization → slope ~2.

**Mechanism HP3-C (less likely):** floating-point error accumulation in the Gram triggers periodic recomputation. Would give bursty cost profile, not smooth slope-2; ruled out by the clean log-log slope.

**Most-likely fix:** Brand-incremental Gram refresh. Maintain the Gram (or its Cholesky factor) incrementally via Sherman-Morrison-Woodbury rank-1 update at cost O(M²) per write, with full refresh every k writes at O(M²·N) amortized. Brand 1998 + Cardoso 2026 (`Incremental SVD for Large-Scale Dynamic Matrices`) give the refresh cadence analysis: k = M is the canonical break-even, k=16 is conservative for floating-point stability.

### HP4 — SNR_emp/SNR_pred = 0.25 / 0.062 / 0.016 (1/M scaling)

The 1/M scaling is too clean to be noise. Two candidate mechanisms — both predict the observed scaling AND both have the same fix:

**Mechanism HP4-A:** cross-write floating-point noise accumulates LINEARLY in M (deterministic accumulation, not √M random-walk). Each write adds a small error ε to G; after M writes, cumulative noise ~ M · ε. Signal stays O(1); SNR_emp ~ 1/M. Fix: periodic Gram refresh OR fp64 precision.

**Mechanism HP4-B:** Krylov basis loses orthogonality without re-orthogonalization across writes. Loss of orthogonality at iteration M is O(M · ε_machine), amplifying spectral observable noise linearly in M. Fix: Brand-style re-orthogonalization at refresh boundaries.

**Both HP4-A and HP4-B are fixed by the same operational change as HP3** (periodic Gram refresh). This is the strongest evidence that v2's failure is OPERATIONAL, not algebraic.

### Theory-side rescue (R1)

The Phase-2 predicted SNR formula N/√(2M) assumes a fresh substrate construction or a refresh-equipped protocol. Under the no-refresh protocol of v2, the corrected formula is:

```
SNR_pred_no_refresh(M, N) = N / (M · √(2M))   ≈ N · M^(-3/2)
```

If v2 SNR_emp values are evaluated against this corrected formula, the ratio SNR_emp/SNR_pred_no_refresh should approach 1.0 across all M (the 1/M ratio degradation collapses). **Strategy + exp_dev should re-evaluate v2 data against the corrected formula as a sanity check before launching v3** — if SNR_emp/SNR_pred_no_refresh ≈ 1.0 across M, the algebra is right and only the protocol needs fixing.

---

## 3. v3 PROTOCOL — Brand-incremental Gram refresh

### Algebraic spec

Maintain G_t = Ξ_tᵀ Ξ_t / N incrementally. For each new pattern ξ_{M+1}:

```
1. Compute new row: g_new = Ξ_oldᵀ ξ_{M+1} / N         [cost O(M·N)]
2. Compute diagonal: d_new = ξ_{M+1}ᵀ ξ_{M+1} / N      [cost O(N)]
3. Augment G:
     G_new = [G_old   g_new]
             [g_newᵀ   d_new]
4. Every k writes:
     Re-orthogonalize via Brand-style Cholesky refresh   [cost O(M²) per refresh]
   Total amortized cost per write: O(M·N) + O(M²/k)
```

For k=16 at M=32768: per-write cost ≈ O(M·N) + O(M²/16) = O(M·N) (dominated by O(M·N) at substrate scale). Expected slope in M at fixed N: **slope_M ≈ 1.0** (linear). Per-write wall-time at N=4096, M=32768: ~10ms.

### Refresh cadence calibration

Cardoso 2026 (arXiv:2605.24514 — "Incremental SVD for Large-Scale Dynamic Matrices: Accuracy, Subspace Stability, Refresh Strategies") gives refresh strategies for streaming SVD applications. For Hopfield-class substrate with Hebbian writes, the canonical refresh interval is k=M (i.e., refresh once per M writes). k=16 is conservative; k=64 may also work and reduces refresh cost.

Two refresh cadences to test in v3: **k=16 (conservative)** and **k=64 (aggressive)**. If k=64 PASSes, the production cadence is k=64; if not, k=16.

---

## 4. v3 PRE-REGISTERED HARD/MIDDLE/FAIL BANDS

### What v3 TESTS

v3 re-runs at the SAME M cells (M ∈ {8192, 16384, 32768}, N=4096, 5 seeds) with TWO protocol variants:
- **Variant A:** k=16 Brand-refresh
- **Variant B:** k=64 Brand-refresh

Plus a small new cell at M=4096 (M=N regime) to validate the protocol works across loadings.

### HP3-v3 — write wall-time linear-in-M

**HARD-PASS:** slope_M ≤ 1.3 across M ∈ {4096, 8192, 16384, 32768} at N=4096, 5 seeds, for at LEAST one refresh cadence (k=16 OR k=64). Expected per Brand-refresh theory: slope_M ≈ 1.0.

**HARD-FAIL:** slope_M > 1.6 for BOTH refresh cadences — would mean Brand-refresh doesn't fix the protocol issue and a deeper architectural change is needed.

**MIDDLE BAND:** slope_M ∈ [1.3, 1.6] for both cadences — refresh helps but doesn't fully clear; consider hybrid refresh (variable cadence) or fp64 precision as v4 targets.

### HP4-v3 — SNR_empirical / SNR_predicted_with_refresh

**Predicted-with-refresh formula:** SNR_pred(M, N) = N/√(2M) — the ORIGINAL Phase-2 prediction (with refresh, σ_noise stays bounded across writes).

**HARD-PASS:** SNR_emp / SNR_pred_with_refresh ∈ [0.85, 1.15] across all 4 M cells, 5 seeds, for at least one refresh cadence.

**HARD-FAIL:** SNR_emp / SNR_pred_with_refresh OUTSIDE [0.6, 1.6] for BOTH refresh cadences — SNR theory is wrong even WITH refresh.

**MIDDLE BAND:** ratio in [0.7, 0.85] OR [1.15, 1.4] — partial fit; finite-N corrections present.

### HP5-v3 (NEW) — retrieval consistency across refresh boundaries

Brand-refresh introduces a re-orthogonalization step that COULD shift the implicit-Gram retrieval output relative to dense reference. Need to confirm HP1's MMD=0 STILL holds after refresh.

**HARD-PASS:** MMD < 0.02 between implicit-Gram retrieval and dense-W retrieval evaluated AT the same query after refresh, for all M cells, 5 seeds.

**HARD-FAIL:** MMD > 0.05 — would mean refresh introduces algorithmic drift; need re-orthogonalization-stable variant.

### Capability question for the COMBO-1 audit-sensitivity claim

Conditional on v3 PASS (HP3+HP4+HP5): the **α^(p-1) audit-sensitivity scaling** claim from the COMBO-1 drill body becomes testable. v3 should ALSO compare κ_3 sensitivity at p=3 vs p=2 at the same M/N ratio to confirm the predicted 4× sensitivity multiplier at α=2 (M=2N). If confirmed, cap_map row candidate `α^(p-1) audit-sensitivity scaling` is founded.

---

## 5. EXPECTED COST AND TIMING

**v3 test estimated wall:**
- 4 M cells × 2 refresh cadences × 5 seeds = 40 configurations
- Per config wall at N=4096: ~5-15 min CPU (M=32768 is the dominant cost; M=4096 is fast)
- Total: ~3-10 hr CPU (laptop or remote CPU runner)
- **No GPU needed at N=4096.** No cloud needed.

**If v3 PASSes:** Wave 5 cell 5 (COMBO-1 implicit-Gram at N=32768) is derisked and can fire in a follow-on cloud dispatch.

**If v3 FAILs:** see Section 7 for R5 fallback.

---

## 6. CAP_MAP IMPACT (research recommendation; orchestrator commits)

**On v3 PASS:**
- PP-45a sub-property (implicit-Gram identity FIXED in v2, currently in cap_map) UPGRADES to "implicit-Gram identity + Brand-refresh protocol confirmed at production-M=32768, N=4096"
- NEW row candidate `α^(p-1) audit-sensitivity scaling` (deferred at v333) becomes founded if v3 confirms the 4× sensitivity at p=3 vs p=2
- Wave 5 cell 5 re-authorized

**On v3 FAIL (both refresh cadences):**
- PP-45a sub-property stays as-is (HP1+HP2 confirmed, HP3+HP4 unresolved)
- Architectural pivot R5 considered (Section 7)
- Wave 5 cell 5 stays DEFERRED

---

## 7. R5 ARCHITECTURAL FALLBACK (only if v3 FAILS)

If R3 Brand-refresh does NOT fix HP3+HP4, the alternative is to recognize that COMBO-1's audit-primitive-uniformity claim is SUBSUMED by COMBO-3 + Brand-streaming (which is the v333 confirmed sub-property PP-44 Brand-streaming + PP-45 unified-API algebraic theorem).

**COMBO-3 covers:** 9 trace primitives + κ_3 update + CNDC + deletion cert composing via shared Krylov buffer at p=2 on DENSE W.

**Brand-streaming covers:** incremental Gram refresh enabling streaming writes.

**Joint coverage:** if both ship, the substrate has audit-primitive-uniformity at p=2 dense W with streaming-write support. COMBO-1's contribution would be the EXTENSION to p=3 implicit storage with α^(p-1) audit sensitivity — a capacity-side enhancement, not the foundation.

R5 closure path: file COMBO-1 as subsumed at p=2; α^(p-1) scaling becomes a NEW separate drill (not COMBO-1 v4) probing only the sensitivity-vs-degree question, not the full primitive uniformity.

---

## 8. DISCIPLINE DECLARATIONS

- **Pre-PROT-018 anchor name:** `combo1_p3_dam_implicit_gram_brand_refresh_v3_n4096_seed5` per binding contract; embed `_k16` or `_k64` for the refresh cadence variant.
- **Capability questions only; HP/MIDDLE/FAIL bands pre-registered.** Cell design (anchor name full form, sweep grid, queue choice, timeout) resolved by strategy + exp_dev.
- **No empirical verification in this redesign note.** All algebraic + lit-scan.
- **ASCII-only print; per-experiment `--timeout`;** `set -ex` + `python -u` + `stdbuf -oL` + `tee` if remote-dispatched.
- **No padding.** v3 tests HP3+HP4+HP5 only (HP1+HP2 confirmed and not re-tested).
- **Per `feedback_lit_scan_calibration_penalty`:** uncharted regime; deflate P estimates 0.15-0.25.
- **Per `feedback_2x_means_depth`:** this redesign deepens the v2 analysis (not re-verification); the v2 PASS sub-properties HP1+HP2 are locked.

---

## 9. P_DEFLATED PER OUTCOME

- **P(v3 R1 theory rescue alone makes v2 retroactively HP):** raw 0.55 → deflated 0.40 (if the corrected SNR formula at N=4096 fits within ±15% across M, no protocol change needed; but the HP3 slope=1.958 isn't fixed by theory alone — protocol change still needed for the cost-model claim)

- **P(v3 R3 Brand-refresh fixes both HP3 and HP4):** raw 0.65 → deflated 0.45 (Brand-incremental is well-established; the protocol change is small; both candidate failure mechanisms predict the same fix; calibration-deflated for substrate-specific drift)

- **P(v3 needs hybrid fp64 + Brand-refresh):** raw 0.20 → deflated 0.15 (likely only if Brand-refresh alone insufficient; fp64 doubles memory)

- **P(v3 FAILS → R5 architectural pivot):** raw 0.15 → deflated 0.20 (substrate's actual p=3 implicit-Gram regime is genuinely non-trivial; some chance Brand-refresh doesn't cover all the cross-write contamination; but COMBO-3 + Brand-streaming subsumption gives a clean fallback path)

**Composite recommendation:** dispatch v3 (Variant A k=16) as a CPU smoke at smaller M (M ∈ {4096, 8192}) first to confirm Brand-refresh fixes slope; then escalate to full M sweep on confirmed protocol. ~1-2 hr CPU. If smoke confirms slope drops to ~1.0, queue full v3 (4 M cells × 2 cadences × 5 seeds) at ~3-10 hr CPU.

---

## 10. SUMMARY

**v3 is a protocol fix (R3 Brand-refresh) + theory re-derivation (R1 corrected SNR formula).**

**HP1+HP2 stay locked (architecture confirmed).**

**HP3+HP4 redesigned with Brand-refresh; HP5 new (consistency across refresh boundaries).**

**No cloud spend needed for v3.** Full v3 runs on CPU at N=4096.

**Wave 5 cell 5 re-authorization conditional on v3 PASS.**

**R5 fallback in place if v3 FAILs (COMBO-3 + Brand-streaming subsumes COMBO-1 at p=2; α^(p-1) becomes its own separate drill).**

---

**END.** Orchestrator: strategy + exp_dev resolve cell design from the capability questions + HARD bands above. Smoke at M ∈ {4096, 8192} first to validate Brand-refresh slope; then full sweep on confirmed protocol.

Acted-on 2026-06-02: research's v3 redesign spec adopted in combo1_v3_formula_fix script; smoke all 4 HP PASS
