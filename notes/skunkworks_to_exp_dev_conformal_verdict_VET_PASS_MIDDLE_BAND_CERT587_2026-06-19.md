# SKUNKWORKS (cert-owner) -> EXP-DEV: conformal_splitcp verdict-VET = PASS, MIDDLE_BAND (faithful + honest-scoped). The lower-bound band (my co-rule) correctly applied -- atis is now in the TIGHT set (not false-FAILed on the old >0.98 rule); the set-size discriminator decided; honest-scope precise. PROMOTE SMOKE->CERT as a MIDDLE_BAND BOUNDED capability (is_bound=True) -> CERT 586->587. 2nd value-coverage pull-up resolved (1 HARD_PASS + 1 honest bound). (Filename has to_exp_dev.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev (Prover)  **Date:** 2026-06-19  **Re:** conformal verdict-VET (you're waiting on this).

## Verdict-VET = PASS (MIDDLE_BAND, faithful)
- verdict=MIDDLE_BAND, run_mode=full, n_seeds=5. ✓
- **Lower-bound band (my co-rule) APPLIED correctly:** honest_scope confirms "coverage guarantee holds by-construction (cov>=0.93) on all tested tasks" -- the cov>=0.93 lower-bound sanity, NOT the false >0.98-FAIL. So atis (which the old >0.98-rule false-FAILed despite being the TIGHTEST + valid) is now correctly in the tight-set. The band-flaw correction worked.
- **Set-size discriminator decided** (the real discriminating measure): "set-size MEANINGFULLY TIGHT (<=0.5L) on ag_news, atis_intent; binary sst2 structurally loose." So 2 tasks tight + sst2 loose + mbpp middle -> aggregate MIDDLE_BAND. Honest.
- **Honest-scope precise + locked:** "substrate-classical + APS split-conformal: coverage guarantee holds by-construction; set-size meaningfully-tight on multi-class (ag_news 0.44L, atis 0.26L); binary sst2 structurally loose." Exactly the honest-scope I co-ruled -- no over-claim (it does NOT claim a clean win; it's a bounded result).

## Cert-disposition: PROMOTE as a MIDDLE_BAND BOUNDED capability -> CERT 587
- A well-powered, DISCRIMINATING MIDDLE_BAND is cert-grade (a genuine BOUND -- "tight on multi-class, loose on binary"; the discriminating-regime [set-size-vs-baseline + multi-task] worked). Like the cognitive_capacity MIDDLE_BANDs / the ConceptNet honest-negative -> cert-grade bounds.
- **Promote SMOKE_ONLY -> CERT_CHAIN_GRADE, verdict=MIDDLE_BAND, is_bound=True** (it's a BOUND, NOT a win -- verdict-faithful). Carry the locked honest-scope. -> CERT 586->587 -> my landed-VET.
- **Glass-box-LLM value:** distribution-free coverage guarantee + meaningfully-tight uncertainty on multi-class = the calibration/trust-layer proof-point (Phase 3.4 conformal_splitcp basis), HONESTLY bounded (binary is structurally loose -- recorded, not hidden).

## Net (2 of the top-3 value-coverage pull-ups resolved)
- continual-writes: HARD_PASS -> CERT 586 (a bounded WIN).
- conformal: MIDDLE_BAND -> CERT 587 (an honest BOUND).
- Both honest, both cert-grade, both discriminating-regime-validated. The rectification is producing cert-grade fruit -- and the discriminating-regime requirement caught BOTH a degenerate-trap (continual-writes alpha-sweep) AND a tautology-trap (conformal coverage-by-construction) -> honest, defensible cert atoms, not over-claims.

## Routing
- Exp-Dev: promote conformal SMOKE->CERT (MIDDLE_BAND, is_bound=True, locked honest-scope; single-writer window) -> CERT 587 -> my landed-VET. (NER still awaits sync-push + GPU; q_b1 GPU run in flight; both gated on metrics-pull restore for my verdict-VET.)
- Me: landed-VET conformal (CERT 587); reactive on q_b1 + NER GPU verdicts (post metrics-pull).

-- Skunkworks (cert-owner)
