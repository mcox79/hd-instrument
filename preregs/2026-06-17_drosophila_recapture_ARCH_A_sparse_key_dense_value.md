# PREREG: Drosophila-MB-sparse RECAPTURE -- ARCH-A sparse-key / dense-value (linear readout preserved)

**Author:** Exp-Dev (Prover)  **Date:** 2026-06-17  **Cert-chain:** STEP-1 design + STEP-2 prereg (-> Skunkworks SCHEMA-VET + Director LOCK before cell-author)
**Drill source:** notes/research_drosophila_MB_sparse_recapture_linear_heteroassociative_2026-06-17.md (R1.1; 22-citation 3x lit-scan)
**Recaptures:** scorecard claim 1 (Drosophila MB sparse f=0.05) -- STEP-4 disposition = GENUINE OVER-CLAIM (HARD_FAIL gap 0.004; mechanism: sparse mismatched to LINEAR heteroassociative readout).

## AMENDMENT 2026-06-17 (smoke verify-before-asserting catch; Skunkworks re-VET PASS + 2 reqs; pending Director re-LOCK)

The first cell-author + smoke (commit a34e7069) caught a DEGENERATE M-grid before FULL: the original M={512,1024,2048}
are ALL >> the linear heteroassociative exact-recall capacity (~0.14N=143 at N=1024) -> exact-recall(cos>=0.9)
saturates to ~0 for EVERY f_k INCLUDING the f_k=1.0 dense baseline -> the delta=0 MIDDLE_BAND would be an
OVER-CAPACITY ARTIFACT, NOT a real "sparse-key gives no gain" finding. This is verify-before-asserting at the smoke
layer (NO false finding reported). Director RATIFIED; Skunkworks re-VET = PASS. Amendment folded here:

- **M-SWEEP around capacity (v2 fine-sampled):** M in {16,32,64,128,192,256,288,320,352,384,416,448,480,512}.
  SMOKE FINDING (2nd verify-before-asserting catch, non-blocking resolution): the EMPIRICAL exact-recall cliff
  (cos>=0.9 + sign readout) sits at alpha~0.25-0.5 -- HIGHER than the textbook 0.14N=143 (the hard cos threshold +
  sign readout raise effective exact-recall capacity). The coarse {...,256,512} grid had NO point in the transition
  (dense=1.0 at M256 -> ~0 at M512), so the anchor snapped into the zero-zone. Fine-sampling [256,512] in steps of
  32 places grid points ON the graded cliff; smoke now anchors at M=384 (dense exact-recall=0.516~0.5; interp
  cross=385.8) with a NON-DEGENERATE primary comparison (f_k=0.05=0.508 vs f_k=1.0=0.516). (Extends Skunkworks's
  optional finer-mid-cliff suggestion to the empirically-located cliff; same metric/anchor-rule/bands.)
- **REQ-1 (pre-registered deterministic anchor RULE):** anchor M = the grid-M NEAREST the point where the dense
  f_k=1.0 EXACT-recall FIRST crosses 0.5 (scan increasing M; linear-interpolate the crossing between bracketing grid
  points; snap to nearest grid M). Fallback (no clean crossing on the grid): grid-M minimizing |dense_exact-0.5|.
  This RULE is FIXED PRE-RUN (not an M cherry-picked after seeing curves -> removes the anchor-selection DoF).
- **REQ-2 (primary metric = exact-recall; per-bit-acc secondary-only):** PRIMARY verdict is EXACT-RECALL at the
  anchor M (the capacity claim IS exact pattern recall). PER-BIT-ACCURACY (mean component match-rate; continuous,
  non-degenerate) is SECONDARY / DIAGNOSTIC ONLY -- it supports + explains but does NOT gate VALIDATED (a per-bit
  gain does NOT imply exact-recall capacity gain; promoting it would be proxy substitution = the Goodhart trap).
- KEPT unchanged: Ask-3 f_k=1.0 true-dense control; Ask-4 N=4096 confirm-before-VALIDATED; recapture_of provenance;
  HONEST_BOUNDED tiering; honest-negative-acceptable framing.

(The Design + Pre-registered-bands sections below are superseded by this AMENDMENT where they conflict on M-grid /
anchor / primary-metric; all other content stands.)

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
READOUT: recall_i = sign(W @ key_i). PRIMARY = exact-recall rate (fraction of M with cosine(sign(recall),val) >=
   0.9) -- the cert metric, DECIDES verdict. SECONDARY/diagnostic = per-bit-accuracy (mean component match-rate;
   continuous, non-degenerate) -- supports/explains only, does NOT gate VALIDATED (REQ-2).
LOAD sweep (AMENDED v2): M in {16,32,64,128,192,256,288,320,352,384,416,448,480,512} (fine-sampled across the
   EMPIRICAL exact-recall cliff at alpha~0.25-0.5; see AMENDMENT). HARD-PASS band anchored at the PRE-REGISTERED
   anchor M (dense f_k=1.0 exact-recall ~0.5; REQ-1), NOT a fixed M (the old fixed M=1024 sat in the degenerate
   over-capacity zero-zone). Smoke anchors at M=384.
SEEDS: smoke = 1 seed; FULL = 5 seeds (cert-chain-grade target: full-mode >=3 seeds).
COMPUTE: LAPTOP super-fast bucket (N=1024 -> W is 1024x1024 ~ 1M entries; M<=2048 pairs; no large NxN/FFT;
   per USER compute policy this is the laptop bucket, NOT remote). Smoke ~seconds; FULL ~minute.
```

## Pre-registered bands (from drill sec (c); tightened to exact-recall cert metric)

```
PRIMARY comparison (Ask-3 + AMENDMENT): at the PRE-REGISTERED anchor M (= grid-M nearest where dense f_k=1.0
   EXACT-recall first crosses 0.5; REQ-1), EXACT-recall at f_k=0.05 vs the f_k=1.00 TRUE-DENSE baseline (NOT
   f_k=0.50, which is itself half-sparse). Test = "sparse-key beats the substrate's DENSE baseline" at the
   mid-cliff where the comparison is actually measurable (not the over-capacity zero-zone).

HARD-PASS (RECAPTURE):   exact-recall(f_k=0.05, anchorM) >= exact-recall(f_k=1.00, anchorM) + 0.05 (>= +5pp),
                          5/5 seeds AND no degenerate lone single-point spike across f_k at the anchor.
HARD-FAIL (REFUTED):     exact-recall(f_k=0.05, anchorM) <= exact-recall(f_k=1.00, anchorM) - 0.03 (<= -3pp) ->
                          sparse-key gives NO exact-recall gain (or hurts) vs the true-dense baseline in the
                          linear regime; honest-negative (verdict HONEST_BOUNDED); row closes at bipolar-value
                          end; next = ARCH-B (softmax).
MIDDLE_BAND:             between -3pp and +5pp vs f_k=1.00 at the anchor -> sparse-key neutral; not a recapture.

SECONDARY (diagnostic only -- does NOT decide verdict; REQ-2): report (a) exact-recall(f_k, M) full grid over
   {0.05,0.10,0.20,0.50,1.00} x {16,32,64,128,192,256,512}; (b) per-bit-accuracy full grid (same axes). The
   per-bit grid reveals a SHIFTED sparse cliff (the real capacity-gain signature) + makes the f_k surface
   visible where exact-recall saturates. Informs ARCH-B decision + cap_map METHOD-CONTINGENT bump. Per-bit-acc
   is NEVER promoted to a verdict input (no proxy substitution / Goodhart).
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
