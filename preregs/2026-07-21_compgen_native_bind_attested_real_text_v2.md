# Pre-reg: compgen_native_bind_attested_real_text_v2

**Filed:** exp_dev, 2026-07-21. Cell: `experiments/exp_compgen_native_bind_attested_real_text_v2.py`.
The earnable-CG shot: native role-filler binding compositional generalization on ATTESTED real-text
role-combinations vs a FAIR shared-readout flat baseline, on genuinely-hard real geometry. Fixes the 3
flaws that landed the prior real-text cell (compgen_native_bind_real_text_v1, atom 29429) at MEASURED-
MECHANISM (VETs a573d0ab / a7e1d20e). LOCAL-ONLY (no push, no store, no atom bank).

## The 3 VET-named requirements (all must be met)
1. HELD-OUT = ATTESTED real-text combinations (not synthetic samples over real pools). Gold SVO triples
   extracted from UD-EWT gold dependency parses (active nsubj+obj / passive nsubj:pass+obl:agent = GOLD
   roles, no parser confound). A concept attested in BOTH roles is held out in ONE role: all its held-out-
   role occurrences removed from train, become the test set. Every held-out (concept,role) is (a) attested
   in real text AND (b) provably absent from training. Verified in self-test: 0 breaches.
2. FAIR shared-readout flat baseline that COULD in-principle generalize (NOT per-role heads / structural-0).
   Flat = shared filler-emb + learned compose + role-query MLP scoring every candidate via Q_role.E_cand
   (single shared output space). Positive control `flat_oracle` (flat trained WITH held-out visible) must
   recover the combos -> proves the readout is capable -> flat's split failure is generalization, not
   architecture.
3. Genuinely-hard-in-dist regime (real geometry, not cosmetic). Richer PPMI-SVD distributional embeddings
   (non-orthogonal similarity/polysemy/frequency). Difficulty swept by TRAINING-DATA FRACTION (a FAIR axis:
   both arms share the same data + full capacity; native's data-efficiency is a fair advantage). Must locate
   a fraction where native_ind in [0.60,0.90] AND native_ho still generalizes.

## Compute architecture
Sequential-CPU justified: tiny complex64 matmuls (V~492, N=256), MLP over ~600 triples; full 3-seed x
5-fraction x 4-arm run = ~95s wall foreground. No GPU batching benefit at this scale. Storage: no_storage
(no bundled-vs-sharded axis; per-example compose). LOCAL foreground-to-completion (no detached fit).

## Arms (one contrast = binding mechanism on/off; gold roles = confound control)
- A native_bind_shared   : shared LEARNED encoder real_feat->phase + FIXED FHRR binding  [MECHANISM]
- B flat_shared_readout  : shared filler-emb + role-query MLP over shared candidates      [FAIR BASELINE]
- C native_bind_tied     : ROLE-SPECIFIC encoders (E_a, E_p)                              [free-algebra locus]
- D native_bind_scramble : A decoded with RANDOM role keys                                [MUST-FAIL lesion]
- flat_oracle            : flat trained WITH held-out visible                             [fair-baseline capability control]

## PRE-REGISTERED CG-vs-MM criterion (bands)
HARD-PASS (CG_ATTESTED_REAL_TEXT) requires ALL:
1. FAIR-COMPARABLE (full data): native_ind >= 0.85 AND flat_ind >= 0.80 (flat competent, not structural-0)
   AND native_ho_full - flat_ho_full >= 0.30.
2. HARD-IN-DIST regime EXISTS: a fraction with native_ind in [0.60,0.90] where native_ho >= flat_ho + 0.15
   AND native_ho >= 25*chance (held-out still generalizes; does NOT collapse to flat).
3. LEARNING CURVE rises: native_ho_init <= 0.10 (near chance) AND rise >= 0.30 (learned, NOT construction).
4. flat_oracle_ho >= 0.60 (fair-baseline readout IS capable).
5. scramble_ho <= 0.05 (binding lesion collapses).
6. geometry off|cos| >= 1.5x random AND max off|cos| >= 0.5 (real non-orthogonal geometry + confusable tail).

HARD-FAIL: native_ho_full <= flat_ho_full + 0.10 (no capability) OR scramble_ho > 0.15 OR flat_oracle_ho <
0.40 (readout structurally-0 = unfair baseline) OR geometry degenerate.
MIDDLE_BAND (MEASURED_MECHANISM): native beats fair-flat but a CG criterion misses.

## Difficulty-on / can-fail (design gate)
- REAL baseline: FAIR shared-readout flat (not strawman; oracle-verified capable).
- CAN-FAIL: native no better than fair-flat on attested held-out -> HARD_FAIL; OR no hard-in-dist regime; OR
  held-out not attested-novel (self-test asserts 0 breaches).
- DIFFICULTY-ON: data-scarcity fraction pushes native_ind into [0.6,0.9]; geometry non-degenerate.
- ONE-VARIABLE: A vs C = shared vs role-specific encoder; A vs B = fixed-binding vs learned-flat composition.

## SCHEMA-VET fields
- arms_differ_verified: true (AF hash-test on decode signatures)
- final_metrics_atomicity: tmp_replace (AH)
- cardinality_ok: true (EXPECTED_N_UNITS = n_frac * n_seed * n_arms)
- crlb_n/a: classification-accuracy discriminator; bands margin-based vs chance=1/V (feasibility ok)
- baseline_in_band: flat competent full-data + fails held-out; native sweeps [0.6,0.9]
- discriminator survives scale: smoke uses FULL geometry (V~492,N=256) + FULL epochs (generalization emerges
  late/grokking-like; epoch count is load-bearing), reduces only seeds+fractions
- deterministic_seeding: fixed int seeds + sorted() splits + index-derived RNG; no hash()-seeded RNG
- progress_logging: line_buffered_stdout; wall ~95s (no 30min heartbeat needed)
- defensive_error_checking: except SystemExit/KeyboardInterrupt before except Exception; crash metrics; atomic write

## Known honest caveats (for VET)
- native_ho is decode-COUPLED to native_ind (same binding-cleanup SNR) -> no single point with hard-in-dist
  AND high-ABSOLUTE held-out; native_ho reaches 0.84 only as native_ind saturates. BUT native_ho stays
  20-214x chance and infinitely-above-flat at every hard point (does NOT collapse -> CG not MM by the
  "rides-down-to-chance" test).
- At the hardest fractions flat_ind is very low (<0.25) = weaker learner; the cleanest fair-hard co-occurrence
  is frac~0.60 (native_ind~0.83, flat_ind~0.46 both struggling, native_ho~0.43 vs flat 0.00).
- tied partially generalizes via distributional r-geometry (not at chance); free-algebra rebuttal rests
  primarily on the learning curve (init~chance) + flat's failure, with tied as supporting margin.
