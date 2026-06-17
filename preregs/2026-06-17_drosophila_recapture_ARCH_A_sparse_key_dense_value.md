# PREREG: Drosophila-MB-sparse RECAPTURE -- ARCH-A sparse-key / dense-value (linear readout preserved)

**Author:** Exp-Dev (Prover)  **Date:** 2026-06-17  **Cert-chain:** STEP-1 design + STEP-2 prereg (-> Skunkworks SCHEMA-VET + Director LOCK before cell-author)
**Drill source:** notes/research_drosophila_MB_sparse_recapture_linear_heteroassociative_2026-06-17.md (R1.1; 22-citation 3x lit-scan)
**Recaptures:** scorecard claim 1 (Drosophila MB sparse f=0.05) -- STEP-4 disposition = GENUINE OVER-CLAIM (HARD_FAIL gap 0.004; mechanism: sparse mismatched to LINEAR heteroassociative readout).

## Honest-recapture framing (load-bearing; per RECAPTURE central discipline)

This is NOT a re-run of the failing config (sparse + linear readout -- STEP-4 says that won't rescue). ARCH-A
tests a GENUINELY DIFFERENT method: SPARSE-KEY / DENSE-VALUE (sparsity governs the KEY/routing; value stays
dense bipolar; linear W = sum val key^T + argmax-cosine readout PRESERVED). It is the only fork that preserves
the substrate's linear-readout product positioning. HONEST-NEGATIVE IS AN ACCEPTABLE OUTCOME: a HARD-FAIL
confirms "sparse coding gives no capacity gain in the linear-readout regime; the dense-bipolar baseline IS the
right capacity baseline; recapture needs a supra-linear selection step (ARCH-B) or is bounded" -- a real
finding that honestly closes the bipolar-value end of the cap_map row. We are TESTING recapture, not forcing it.
P_deflated = 0.35 (drill; likely-fail-leaning) -- we go in expecting either outcome is informative.

## Design (Exp-Dev owns all params per hand-off autonomy)

```
SUBSTRATE: N = 1024 dense bipolar (+/-1) baseline (per drill; substrate-canonical small-N).
KEY encoding: TopK sparse bipolar. active-fraction f_k in {0.05, 0.10, 0.20, 0.50, 1.00}.
   - per key: k = round(f_k * N) positions chosen (seeded random per key); each active position = random +/-1;
     inactive positions = 0.
   - f_k=1.00 = FULLY-DENSE bipolar = the substrate's CANONICAL dense baseline (Ask-3 fix: the TRUE-dense
     control; ALL N positions +/-1). f_k=0.05 = Drosophila operating point. f_k=0.50/0.20/0.10 = intermediate
     sparsity points (NOTE: f_k=0.50 is itself 50%-sparse, NOT a dense control -- per Skunkworks Ask 3).
VALUE encoding: DENSE bipolar (+/-1), N-dim -- HELD DENSE to ISOLATE the sparse-KEY variable (per drill reco).
STORE: W = sum_{i=1..M} val_i (outer) key_i^T   (linear outer-product; PRESERVED -- the substrate's host math).
READOUT: recall_i = sign(W @ key_i); accuracy = mean cosine(recall_i, val_i) thresholded, OR exact-recall rate
   (fraction of M with cosine(recall_i, val_i) >= 0.9). Report BOTH; exact-recall is the cert metric.
LOAD sweep: M in {512, 1024, 2048}  (= N/2, N, 2N; the HARD-PASS band is anchored at M = N = 1024).
SEEDS: smoke = 1 seed; FULL = 5 seeds (cert-chain-grade target: full-mode >=3 seeds).
COMPUTE: LAPTOP super-fast bucket (N=1024 -> W is 1024x1024 ~ 1M entries; M<=2048 pairs; no large NxN/FFT;
   per USER compute policy this is the laptop bucket, NOT remote). Smoke ~seconds; FULL ~minute.
```

## Pre-registered bands (from drill sec (c); tightened to exact-recall cert metric)

```
PRIMARY comparison (Ask-3 fix): at M = N = 1024, exact-recall at f_k=0.05 vs the f_k=1.00 TRUE-DENSE baseline
   (NOT f_k=0.50, which is itself half-sparse). This makes the test "sparse-key beats the substrate's DENSE
   baseline" = the actual claim, not "5%-sparse beats 50%-sparse".

HARD-PASS (RECAPTURE):   acc(f_k=0.05, M=1024) >= acc(f_k=1.00, M=1024) + 0.05 (>= +5pp absolute), 5/5 seeds
                          AND the f_k -> accuracy curve is monotone-or-flat (no degenerate single-point spike).
HARD-FAIL (REFUTED):     acc(f_k=0.05, M=1024) <= acc(f_k=1.00, M=1024) - 0.03 (<= -3pp) -> sparse-key gives
                          NO gain (or hurts) vs the true-dense baseline in the linear regime; honest-negative
                          (verdict HONEST_BOUNDED); row closes at bipolar-value end; next = ARCH-B (softmax).
MIDDLE_BAND:             between -3pp and +5pp vs f_k=1.00 -> sparse-key neutral; not a recapture; bounded.

SECONDARY (capacity-curve): report exact-recall(f_k, M) full grid {0.05,0.10,0.20,0.50,1.00} x {512,1024,2048}
   so the capacity-vs-sparsity surface is visible (informs ARCH-B decision + cap_map METHOD-CONTINGENT bump).
```

## Provenance / verdict (incl. Skunkworks R3-framework-VET 2 refinements)

- metric_type: exact-recall accuracy (+ cosine secondary); AGGREGATE over the f_k x M grid.
- verdict mapping (refinement 2 -- honest-negative tiers correctly, NOT dropped/ARCHIVE-as-worthless):
   HARD-PASS band  -> verdict PASS (recapture; -> VALIDATED-eligible at cert-grade).
   HARD-FAIL band  -> verdict HONEST_BOUNDED (NOT bare HARD_FAIL): the LOAD-BEARING finding "sparse-key /
      dense-value / linear-readout does NOT recapture capacity; the row is bounded to needing a supra-linear
      selection step (ARCH-B)". relevance_tier reflects the bounded finding (it IS substrate-self-knowledge),
      headline preserved. (Per Skunkworks point 2; the atomizer VERDICT_SET maps HONEST_BOUNDED.)
   MIDDLE band     -> verdict MIDDLE_BAND (neutral; sparse-key not a recapture; bounded).
- recapture provenance link (refinement 1 -- makes "genuinely-different" AUDITABLE from the atom):
   recapture_of          = scorecard claim 1 / EXP_substrate_drosophila_mb_sparse_single_modulator_v1 (HARD_FAIL gap 0.004)
   failing_config_avoided = raw sparse-CODING expecting bundle-capacity-gain through a LINEAR heteroassociative
                            readout with NO encoder-threshold / supra-linear selection (the STEP-4 mechanism)
   method_delta          = sparsity moved to the KEY side only (TopK routing/indexing); VALUE held DENSE bipolar;
                            linear W=sum val key^T + argmax-cosine PRESERVED -- tests sparse-as-routing, NOT
                            sparse-as-bundle-capacity (a genuinely different hypothesis, not a re-run/tune)
   (cell writes these into metrics.json so the EXP atom carries them; Skunkworks VETs populated at ingest.)
- FULL-mode 5-seed -> CERT_CHAIN_GRADE provenance target.
- method-contingent (METHOD + N axes): result is the envelope OF ARCH-A (sparse-key/dense-value/linear-readout)
  AT N=1024; ARCH-B (softmax readout) + ARCH-C (Willshaw) are separate forks (NOT tested here).
- N-GATE before VALIDATED (Ask 4): a HARD-PASS at N=1024 is the first decisive test but is N-CONTINGENT. The
  original claim/HARD_FAIL was at N=4096 -> a N=1024 HARD-PASS MUST be CONFIRMED at N=4096 (the claim's N)
  before scorecard claim-1 -> VALIDATED. N=4096 confirm = remote (W is 4096x4096 ~ 16M; heavier; per compute
  policy -> remote, NOT the laptop super-fast bucket). So: N=1024 run NOW (laptop, decisive first test); on
  HARD-PASS, N=4096 confirm (remote) before VALIDATED.

## Cert-chain next steps

1. Skunkworks SCHEMA-VET: method-genuinely-different (YES: sparse-KEY not sparse+linear-rerun); falsifiable
   (YES: +5pp/-3pp bands); metric-matches-semantic (exact-recall = the capacity claim; no Goodhart proxy);
   cert-criteria sufficient (5-seed full-mode). + confirm the dense-control (f_k=0.50) is the right baseline.
2. Director STEP-2 prereg-LOCK.
3. Exp-Dev cell-author (experiments/exp_drosophila_recapture_arch_a_*.py) + verification/ scaffold-free witness
   per CLAUDE.md + smoke-gate -> FULL (laptop super-fast) -> verdict.
4. On HARD-PASS: re-atomize the new EXP record (cert-grade) -> per-cell re-audit -> scorecard claim-1 status.
   On HARD-FAIL: file honest-negative; drill ARCH-B (softmax readout) per the drill's next-step.

## Note: 2nd recapture (Tier-6 charLM; R1.2 handoff just arrived) -- design at R3-proper

charLM HD-hybrid recapture is HEAVIER (char-LM training; NOT laptop-super-fast -> R4 remote). I'll design its
prereg after reading the R1.2 drill + (per honesty) it goes to remote execution tomorrow. ARCH-A (this prereg)
is the laptop-runnable FIRST recapture -- can land a decisive result TODAY post-LOCK.

-- Exp-Dev (Prover)
