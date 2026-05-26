# Prereg — F-6 Boolean noise-stability + KKL anchor for 2-coset Kerdock — 2026-05-24

## Origin

- Routing note: `notes/exp_dev_to_queue_F6_boolean_noise_stab_2026-05-24.md` (no parseable schema — orchestrator emitted `shipment_record` on first dispatch; resolved by orchestrator main thread inline this turn).
- Research source: `notes/research_new_continents_deep_drill_2026-05-24.md` Section 2 (Boolean function analysis deep drill) + Section 2.5 (concrete anchor proposal) + Section 5 (Hopfield-cleanup risk).
- Cap-13 candidate #3 of the new-continents triple (F-14 Tropical + F-4 Clifford-TN + F-6 Boolean).

## Hypothesis

Kerdock 2-coset codewords are quadratic bent functions; their Walsh-Hadamard spectra concentrate Fourier mass at low |S|. Per Solov'eva-Tokareva 2008, Carlet survey, Mesnager bent-function invited paper. The drill argues Stab_rho(f_Kerdock) = rho^2 at degree-2.

H0: Kerdock 2-coset readout f satisfies Stab_rho(f) = rho^2 (within experimental noise) and the KKL inequality I_max(f) >= Var(f) log_2(N) / N holds with equality (within numerical noise) for sampled codewords.

H1 (null): Substrate has Fourier mass outside degree-2 OR substrate not at KKL-tight; bent assumption contradicted.

## Falsifiability bands (verbatim from drill Section 2.5)

- **HARD PASS** (BOOLEAN_NOISE_STAB_BENT_PASS): PRE-cleanup |Stab_rho - rho^2| <= 0.02 at rho=0.9 (target rho^2 = 0.81); AND KKL slack <= 0.30.
- **PARTIAL** (BOOLEAN_NOISE_STAB_PARTIAL): PRE-cleanup met but POST-cleanup |Stab_rho - rho^2| > 0.02 (cert applies only to PRE-cleanup readout); OR PRE-cleanup |dev| in (0.02, 0.10] (middle band).
- **HARD FAIL** (BOOLEAN_NOISE_STAB_HARD_FAIL): PRE-cleanup |Stab_rho - rho^2| > 0.10; OR KKL slack > 0.30.

Risk per drill Section 5: Hopfield cleanup is degree-O(N) algebraically; may inject higher-degree Fourier content. Anchor reports both PRE-cleanup and POST-cleanup Stab_rho separately; PRE-cleanup is the primary falsifiable test of the bent-function claim. POST-cleanup MC under cleanup-applied-to-noisy-vector is filed as FOLLOW-UP (full substrate state cleanup is O(N * n_samples) memory and would re-shape the test; current cleanup variant in the script returns identical-to-pre value pending follow-up dispatch).

## Parameters

- N = 1024 (production; smoke at N = 256 -- per [[feedback-no-smoke]] smoke is gated on PRE-cleanup match within 2% AND KKL slack within 30%)
- 10 codewords sampled from 2N = 2048 (smoke: 4 codewords from 512)
- 20000 MC samples per (codeword, rho) cell (smoke: 5000)
- rho_grid = {0.7, 0.8, 0.9}; rho_primary = 0.9 (verdict bands evaluated at rho_primary)
- seed = 17

## Methods

1. Build 2-coset Kerdock codebook via `make_kerdock_2coset_codebook` (reused from `experiments/exp_wave14v_erase_kerdock_v2.py`).
2. For each sampled codeword c (treated as Boolean function f: {0,1}^m -> {-1,+1}):
   - Walsh-Hadamard transform of c gives f_hat(S) for all 2^m subsets.
   - Plancherel Stab_rho_walsh(f) = sum_S rho^|S| * f_hat(S)^2.
   - Monte Carlo Stab_rho_mc(f) sampled via bit-flip channel y = x XOR flip_mask with flip_mask drawn bit-wise indep Bernoulli((1-rho)/2).
   - Per-bit influence Inf_i(f) = Pr_X[f(X) != f(X^(i))] over uniform X.
   - KKL bound: log_2(N)/N (Var=1 for balanced bent codewords).
3. Report PRE-cleanup and POST-cleanup separately (POST is currently a placeholder returning PRE due to memory constraint on per-sample cleanup; follow-up anchor planned).
4. Verdict via thresholds above.

## Self-test gates (per [[feedback-strategy-spec-formula-selftests]])

- Verdict logic across 6 canonical cases (HARD_PASS / PARTIAL / HARD_FAIL / KKL_FAIL / MIDDLE_BAND / INCONCLUSIVE).
- Walsh anchor: constant +1 codeword -> Stab_rho_walsh = 1 for all rho (Plancherel identity).
- Walsh anchor: chi_{1}(x) = (-1)^x_0 codeword -> Stab_rho_walsh = rho^1 = rho (single-Fourier-coefficient sanity check).
- MC vs Walsh consistency: chi_1 Stab_rho_mc(rho=0.9, n=20000) within +/- 0.02 of 0.9.

All three numerical anchors MUST pass for self-test to clear.

## Honest framing per [[feedback-no-smoke]]

- PRE-cleanup PASS: HIGH confidence (mechanism = published bent-function fact + Walsh basis is exact for the codebook).
- POST-cleanup PASS: MEDIUM confidence; the current script's POST-cleanup placeholder is honest about its scope (returns PRE value; full cleanup-injected Stab_rho is a follow-up anchor due to memory constraint).
- KKL tightness on substrate: MEDIUM confidence; tightness needs numerical verification across multiple codewords.

Expected outcome: PRE-cleanup PASS at rho=0.9 with high confidence; KKL tightness likely PARTIAL (substrate may be in the "above the bound by 10-30%" regime, which is BOOLEAN_NOISE_STAB_PARTIAL / MIDDLE BAND not BENT_PASS).

Per drill Section 5 honest assessment: "70-80% Cap 13 with explicit cleanup caveat. Not framed as automatic win."

## Verdict bands (operationalized)

| Outcome | PRE-cleanup MC dev | KKL slack | Tag |
|---------|--------------------|-----------|-----|
| Bent passes | <= 0.02 | <= 0.30 | BOOLEAN_NOISE_STAB_BENT_PASS |
| Bent passes PRE, fails POST | <= 0.02 (PRE) + >0.02 (POST) | <= 0.30 | BOOLEAN_NOISE_STAB_PARTIAL |
| Middle band | (0.02, 0.10] | any | BOOLEAN_NOISE_STAB_PARTIAL |
| Bent assumption violated | > 0.10 | any | BOOLEAN_NOISE_STAB_HARD_FAIL |
| KKL not tight | any | > 0.30 | BOOLEAN_NOISE_STAB_HARD_FAIL |

## Anchor outputs

- `data/exp_wave14_boolean_noise_stab_kerdock_kkl_v1/metrics.json`
- Smoke variant: `data/exp_wave14_boolean_noise_stab_kerdock_kkl_v1_smoke/metrics.json`

## ETA

CPU wallclock estimate per drill Section 2.5: 2-4 hours full run. Walsh transform O(N log N) per codeword + 20000 MC samples per (codeword, rho) cell -> 10 codewords * 3 rho values * 20000 samples * O(m) per sample = O(10 * 3 * 20000 * 10) = ~6e6 ops + O(10 * 1024 * 10) influence ops + O(10 * 1024 * log 1024) WHT ops = on the order of 10 minutes CPU. Conservative timeout 14400s (4 hr) per drill.

## Cap-13 candidate interpretation

Per drill Section 2: "Bent-function noise-stability certificate -- replaces failed Hatano-Sasa IFT path for Cap 3 streaming; closed-form polynomial decay under BSC noise."

If BOOLEAN_NOISE_STAB_BENT_PASS lands: substrate gains a Cap 13 candidate row promotion in the closed-form-Cap-3-erase-cert axis, COMPLEMENTARY to the v181 Cap 13 candidate row (which carries the Tropical + Clifford-TN closed-form-margin program; F-14 Tropical N=4 R2 confirmed earlier today; F-4 Clifford-TN bond-dim-1 MIDDLE BAND).

If BOOLEAN_NOISE_STAB_PARTIAL: PRE-cleanup cert licensed for Cap 1 substrate but POST-cleanup (Cap 3 streaming readout) needs separate anchor.

If BOOLEAN_NOISE_STAB_HARD_FAIL: bent-function assumption contradicted on substrate's Kerdock construction; downgrades Cap-13 claim; audit cap_map for any Cap 1/Cap 3/Cap 8 annotations relying on bent property.
